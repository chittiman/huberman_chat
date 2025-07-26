
import os
from pathlib import Path
from pydantic_models import VideoAnalysis, RAGQuestionSet
from gemini_chat_completion import GeminiChat
from typing import List
import weave
import json
from tqdm import tqdm
from logging import getLogger
logger = getLogger(__name__)
logger.setLevel("DEBUG")

model_name = "gemini-2.5-flash"
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
    chapters_text = chapters_path.read_text(encoding='utf-8')
    chapters_data = json.loads(chapters_text)
    if not chapters_data:
        logger.error(f"No valid chapters data found in {chapters_path}.")
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
    print(f"Questions saved to {questions_path}")

if __name__ == "__main__":
    # Example: process one transcript file
    import random

    weave.init('huberman-chat')
    cur_dir = Path.cwd()
    data_dir = cur_dir / "data"
    chapters_dir = data_dir / "chapters"
    questions_dir = data_dir / "questions"

    rough_dir = data_dir / "rough"
    questions_dir.mkdir(parents=True, exist_ok=True)

    # Pick one .srt file for demonstration
    chapters_files: List[Path] = list(chapters_dir.glob("*.json"))
    if not chapters_files:
        print("No transcript files found in data/chapters.")
    else:
        for chapters_path in tqdm(random.sample(chapters_files,5), desc="Processing transcripts"):
            try:
                # Read the transcript file
                output_path = questions_dir / f"{chapters_path.stem}.json"
                if output_path.exists():
                    print(f"Questions already exist for {chapters_path}, skipping.")
                    continue
                print(f"Generating questions for {chapters_path}...")
                video_id = chapters_path.name.split('.')[0]
                with weave.attributes({'video_id': video_id, 'model': model_name}):
                # Generate questions using GeminiChat
                    generate_questions(chapters_path, output_path)
                    # Generate chapters using GeminiChat
            except Exception as e:
                logger.error(f"Error processing {chapters_path}: {e}")