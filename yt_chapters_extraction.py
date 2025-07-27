
import os
from pathlib import Path
from pydantic_models import VideoAnalysis
from gemini_chat_completion import GeminiChat
from typing import List
import weave
from tqdm import tqdm
import logging
from logging_config import setup_logging

# Configure logging
setup_logging(level=logging.INFO, log_to_file=True, log_file="yt_chapters_extraction.log")
logger = logging.getLogger(__name__)

model_name = "gemini-1.5-flash"
# Setup GeminiChat instance for structured output
gemini_chat = GeminiChat(
    prompts_dir="prompts/chapters_extractor_prompts/json_chapters",
    output_type="structured",
    pydantic_model=VideoAnalysis,
    model_name=model_name
)

if __name__ == "__main__":
    weave.init('huberman-chat')
    cur_dir = Path.cwd()
    data_dir = cur_dir / "data"
    subtitles_dir = data_dir / "subtitles"
    chapters_dir = data_dir / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)

    srt_files: List[Path] = list(subtitles_dir.glob("*.srt"))
    if not srt_files:
        logger.warning("No transcript files found in data/subtitles.")
    else:
        for srt_path in tqdm(srt_files, desc="Processing transcripts"):
            try:
                output_path = chapters_dir / f"{srt_path.stem}.json"
                if output_path.exists():
                    logger.info(f"Chapters already exist for {srt_path.name}, skipping.")
                    continue

                logger.info(f"Processing transcript: {srt_path.name}")
                transcript_text = srt_path.read_text(encoding='utf-8')
                video_id = srt_path.stem

                input_data = {"transcript": transcript_text}

                with weave.attributes({'video_id': video_id, 'model': model_name}):
                    chapters_obj = gemini_chat.complete(input_data)

                output_path.write_text(chapters_obj.model_dump_json(indent=2), encoding='utf-8')
                logger.info(f"Successfully saved chapters to {output_path}")

            except Exception as e:
                logger.error(f"Failed to process {srt_path.name}: {e}", exc_info=True)