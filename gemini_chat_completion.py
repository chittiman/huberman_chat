from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
from jinja2 import Template
from pydantic import BaseModel
from typing import Union, Optional
import logging
import time
from pathlib import Path
from typing import Type
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.genai.errors import APIError, ClientError, ServerError
load_dotenv()
import weave

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiChat:
    def __init__(
        self,
        prompts_dir: str,
        output_type: str = "text",
        pydantic_model: Type[BaseModel] | None = None,
        model_name: str = "gemini-2.5-pro",
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize the GeminiChat class.

        Args:
            prompts_dir: Directory containing prompt markdown files
            output_type: 'text' for regular text output or 'structured' for Pydantic model output
            pydantic_model: Pydantic model class for structured output (required if output_type='structured')
            api_key: Gemini API key (if None, expects GOOGLE_API_KEY in environment)
            max_retries: Maximum number of retry attempts for API calls
            retry_delay: Delay between retries in seconds
        """
        self.prompts_dir = Path(prompts_dir)
        self.output_type = output_type
        self.pydantic_model = pydantic_model
        self.model_name = model_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Validate output type and Pydantic model
        if output_type not in ["text", "structured"]:
            raise ValueError("output_type must be 'text' or 'structured'")
        if output_type == "structured" and pydantic_model is None:
            raise ValueError("pydantic_model must be provided for structured output")

        # Fetch GEMINI_API_KEY from environment
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        # Initialize client (no api_key param)
        self.client = genai.Client()

        # Load prompts (no file params)
        self.system_prompt = self._load_system_prompt()
        self.user_template = self._load_user_template()

    def _load_system_prompt(self) -> str:
        """Load system prompt from markdown file in prompts_dir."""
        filename = "system_prompt.md"
        try:
            file_path = self.prompts_dir / filename
            return file_path.read_text(encoding='utf-8').strip()
        except FileNotFoundError:
            logger.error(f"System prompt file {filename} not found in {self.prompts_dir}")
            raise
        except Exception as e:
            logger.error(f"Error loading system prompt: {str(e)}")
            raise

    def _load_user_template(self) -> Template:
        """Load user prompt as Jinja template from markdown file in prompts_dir."""
        filename = "user_prompt.md"
        try:
            file_path = self.prompts_dir / filename
            return Template(file_path.read_text(encoding='utf-8').strip())
        except FileNotFoundError:
            logger.error(f"User prompt file {filename} not found in {self.prompts_dir}")
            raise
        except Exception as e:
            logger.error(f"Error loading user prompt: {str(e)}")
            raise

    @weave.op(
        name="gemini_chat_completion",)
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((APIError, ClientError, ServerError)),
        reraise=True
    )
    def complete(self, input_data: dict) -> Union[str, BaseModel]:
        """
        Generate completion based on input data.

        Args:
            input_data: Dictionary containing variables for user prompt template

        Returns:
            str if output_type='text', Pydantic model instance if output_type='structured'
        """
        # Render user prompt with input data
        try:
            user_prompt = self.user_template.render(**input_data)
        except Exception as e:
            logger.error(f"Error rendering user prompt: {str(e)}")
            raise

        # Prepare config
        if self.output_type == "structured" and self.pydantic_model:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=self.pydantic_model,
                system_instruction=self.system_prompt
            )
        else:
            config = types.GenerateContentConfig(
                system_instruction=self.system_prompt
            )

        response = self.client.models.generate_content(
            model=self.model_name,
            config=config,
            contents=user_prompt
        )

        if self.output_type == "text":
            try:
                return response.text if response.text is not None else ""
            except AttributeError:
                logger.error("Invalid response format for text output")
                raise
        else:
            try:
                parsed = response.parsed
                if self.pydantic_model is not None:
                    if isinstance(parsed, self.pydantic_model):
                        return parsed
                    elif isinstance(parsed, dict):
                        return self.pydantic_model(**parsed)
                logger.error(f"Unexpected parsed type or missing pydantic_model: {type(parsed)}")
                raise ValueError("Parsed response is not a valid Pydantic model or dict, or pydantic_model is None")
            except Exception as e:
                logger.error(f"Error parsing structured output: {str(e)}")
                raise

# Example usage:
if __name__ == "__main__":
    weave.init('gemini_chat_completion_example')
    from pydantic import BaseModel

    # Example Pydantic model for structured output
    class ResponseSchema(BaseModel):
        answer: str
        confidence: float

    # Initialize with text output
    chat_text = GeminiChat(
        prompts_dir="./prompts/chapters_extractor_prompts/json_chapters",
        output_type="text",
        model_name="gemini-2.5-pro"
    )

    # Initialize with structured output
    chat_structured = GeminiChat(
        prompts_dir="./prompts/chapters_extractor_prompts/json_chapters",
        output_type="structured",
        pydantic_model=ResponseSchema,
        model_name="gemini-2.5-pro"
    )

    # Example input data for template
    input_data = {"query": "What is the capital of France?"}

    # Get text completion
    text_response = chat_text.complete(input_data)
    print("Text response:", text_response)

    # Get structured completion
    structured_response = chat_structured.complete(input_data)
    print("Structured response:", structured_response)