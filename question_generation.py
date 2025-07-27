
import os
from pathlib import Path
from pydantic_models import RAGQuestionSet
from gemini_chat_completion import GeminiChat
from typing import List
import weave
import json
from tqdm import tqdm
import logging
from logging_config import setup_logging

# Configure logging
setup_logging(level=logging.INFO, log_to_file=True, log_file="question_generation.log")
logger = logging.getLogger(__name__)

model_name = "gemini-1.5-flash"
# Setup GeminiChat instance for structured output
gemini_chat = GeminiChat(
    prompts_dir="prompts/question_creation_prompts",
    output_type="structured",
    pydantic_model=RAGQuestionSet,
    model_name=model_name
)

@weave.op(name="generate_questions")
def generate_questions(chapters_path: Path, questions_path: Path):
    """
    Generate questions based on the chapters data.
    :param chapters_path: Path to the chapters JSON file.
    :param questions_path: Path to save the generated questions.
    """
    if not chapters_path.exists():
        logger.error(f"Chapters file {chapters_path} does not exist.")
        return

    try:
        chapters_text = chapters_path.read_text(encoding='utf-8')
        chapters_data = json.loads(chapters_text)
        if not chapters_data or "chapters" not in chapters_data:
            logger.warning(f"No valid chapters data found in {chapters_path}.")
            return

        # Prepare input for GeminiChat
        input_data = {
            "overall_summary": chapters_data.get("overall_summary", ""),
            "chapters": json.dumps(chapters_data.get("chapters", []), indent=2),
            "topics": chapters_data.get("topics", [])
        }

        questions_obj = gemini_chat.complete(input_data)

        # Save output
        questions_path.write_text(questions_obj.model_dump_json(indent=2), encoding='utf-8')
        logger.info(f"Successfully saved questions to {questions_path}")

    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in {chapters_path}. Skipping.")
    except Exception as e:
        logger.error(f"Failed to generate questions for {chapters_path.name}: {e}", exc_info=True)


if __name__ == "__main__":
    import random

    weave.init('huberman-chat')
    cur_dir = Path.cwd()
    data_dir = cur_dir / "data"
    chapters_dir = data_dir / "chapters"
    questions_dir = data_dir / "questions"
    questions_dir.mkdir(parents=True, exist_ok=True)

    chapters_files: List[Path] = list(chapters_dir.glob("*.json"))
    if not chapters_files:
        logger.warning("No chapter files found in data/chapters.")
    else:
        # Process a random sample of 5 files for demonstration
        files_to_process = random.sample(chapters_files, min(5, len(chapters_files)))
        
        for chapters_path in tqdm(files_to_process, desc="Generating questions"):
            try:
                output_path = questions_dir / f"{chapters_path.stem}.json"
                if output_path.exists():
                    logger.info(f"Questions already exist for {chapters_path.name}, skipping.")
                    continue

                logger.info(f"Generating questions for {chapters_path.name}...")
                video_id = chapters_path.stem
                with weave.attributes({'video_id': video_id, 'model': model_name}):
                    generate_questions(chapters_path, output_path)

            except Exception as e:
                logger.error(f"Error in main loop for {chapters_path.name}: {e}", exc_info=True)