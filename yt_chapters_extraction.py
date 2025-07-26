
import os
from pathlib import Path
from pydantic_models import VideoAnalysis
from gemini_chat_completion import GeminiChat
from typing import List
import weave
from tqdm import tqdm
from logging import getLogger
logger = getLogger(__name__)
logger.setLevel("DEBUG")

model_name = "gemini-2.5-flash"
# Setup GeminiChat instance for structured output
gemini_chat = GeminiChat(
    prompts_dir="prompts/chapters_extractor_prompts/json_chapters",
    output_type="structured",
    pydantic_model=VideoAnalysis,
    model_name=model_name
)

if __name__ == "__main__":
    # Example: process one transcript file

    weave.init('huberman-chat')
    cur_dir = Path.cwd()
    data_dir = cur_dir / "data"
    subtitles_dir = data_dir / "subtitles"
    chapters_dir = data_dir / "chapters"
    rough_dir = data_dir / "rough"
    chapters_dir.mkdir(parents=True, exist_ok=True)

    # Pick one .srt file for demonstration
    srt_files: List[Path] = list(subtitles_dir.glob("*.srt"))
    if not srt_files:
        print("No transcript files found in data/subtitles.")
    else:
        # transcript_path = srt_files[1]
        # transcript_text = transcript_path.read_text(encoding='utf-8')
        # video_id = transcript_path.name.split('.')[0]

        for srt_path in tqdm(srt_files, desc="Processing transcripts"):
            try:
                # Read the transcript file
                output_path = chapters_dir / f"{srt_path.stem}.json"
                if output_path.exists():
                    print(f"Chapters already exist for {srt_path}, skipping.")
                    continue
                transcript_text = srt_path.read_text(encoding='utf-8')
                video_id = srt_path.name.split('.')[0]

                # Prepare input for GeminiChat

                # Prepare input for GeminiChat
                input_data = {"transcript": transcript_text}

                with weave.attributes({'video_id': video_id, 'model': model_name}):
                    # Generate chapters using GeminiChat
                    chapters_obj = gemini_chat.complete(input_data)

                # Save output
                output_path.write_text(chapters_obj.model_dump_json(indent=2), encoding='utf-8')
                # save_chapters(chapters_obj, str(output_path))
                print(f"Chapters saved to {output_path}")
            except Exception as e:
                logger.error(f"Error processing {srt_path}: {e}")