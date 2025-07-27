import json
import re
from datetime import timedelta
from pathlib import Path
import logging
from logging_config import setup_logging

# Configure logging
setup_logging(level=logging.INFO, log_to_file=True, log_file="validation.log")
logger = logging.getLogger(__name__)

def parse_srt_timestamp(timestamp_str):
    """Parse SRT timestamp format (HH:MM:SS,mmm) to total seconds"""
    timestamp_str = timestamp_str.split(' --> ')[0].strip()
    time_part, ms_part = timestamp_str.split(',')
    hours, minutes, seconds = map(int, time_part.split(':'))
    milliseconds = int(ms_part)
    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000

def parse_chapter_timestamp(timestamp_str):
    """Parse chapter timestamp format (M:SS or H:MM:SS) to total seconds"""
    timestamp_str = timestamp_str.strip()
    parts = timestamp_str.split(':')
    if len(parts) == 2:
        minutes, seconds = map(int, parts)
        return minutes * 60 + seconds
    elif len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
        return hours * 3600 + minutes * 60 + seconds
    else:
        raise ValueError(f"Invalid timestamp format: {timestamp_str}")

def get_final_transcript_timestamp(transcript_content):
    """Extract the final timestamp from the transcript"""
    timestamp_pattern = r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}'
    timestamps = re.findall(timestamp_pattern, transcript_content)
    if not timestamps:
        raise ValueError("No timestamps found in transcript")
    last_timestamp = timestamps[-1]
    end_time = last_timestamp.split(' --> ')[1]
    return parse_srt_timestamp(end_time)

def validate_timestamps(transcript_file: Path, chapters_file: Path):
    """Main function to validate timestamps for a single pair of files."""
    try:
        transcript_content = transcript_file.read_text(encoding='utf-8')
        chapters_data = json.loads(chapters_file.read_text(encoding='utf-8'))
        
        final_transcript_seconds = get_final_transcript_timestamp(transcript_content)
        
        invalid_timestamps = []
        for chapter in chapters_data.get('chapters', []):
            timestamp = chapter.get('timestamp', '')
            heading = chapter.get('heading', 'N/A')
            try:
                chapter_seconds = parse_chapter_timestamp(timestamp)
                if chapter_seconds > final_transcript_seconds:
                    invalid_timestamps.append(
                        f"Timestamp '{timestamp}' exceeds transcript duration "
                        f"({final_transcript_seconds:.2f}s) for chapter: '{heading}'"
                    )
            except ValueError as e:
                invalid_timestamps.append(f"Parse error for timestamp '{timestamp}': {e}")
        
        if invalid_timestamps:
            for error in invalid_timestamps:
                logger.warning(f"Invalid timestamp in {chapters_file.name}: {error}")
            return False
        else:
            logger.info(f"All timestamps in {chapters_file.name} are valid.")
            return True
            
    except FileNotFoundError as e:
        logger.error(f"File not found during validation: {e}")
        return False
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON format in {chapters_file.name}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred validating {transcript_file.name}: {e}", exc_info=True)
        return False

def validate_all_transcripts_and_chapters():
    """
    Validate all transcript/chapter pairs, logging mistakes to a file.
    """
    subtitles_dir = Path("data/subtitles")
    chapters_dir = Path("data/chapters")
    mistakes_log_path = Path("timestamp_mistakes.log")
    
    failed_files = []

    srt_files = list(subtitles_dir.glob("*.srt"))
    if not srt_files:
        logger.warning("No .srt files found in data/subtitles to validate.")
        return

    logger.info(f"Starting validation for {len(srt_files)} transcript(s)...")

    for srt_file in srt_files:
        json_file = chapters_dir / srt_file.with_suffix('.json').name
        if not json_file.exists():
            missing_msg = f"Missing chapters file for {srt_file.name}"
            logger.warning(missing_msg)
            failed_files.append(missing_msg)
            continue
        
        if not validate_timestamps(srt_file, json_file):
            failed_files.append(srt_file.name)

    if failed_files:
        logger.warning(f"Validation complete. Found issues in {len(failed_files)} file(s).")
        with open(mistakes_log_path, "w", encoding="utf-8") as f:
            for line in failed_files:
                f.write(line + "\n")
        logger.info(f"List of files with errors logged to {mistakes_log_path}")
    else:
        logger.info("Validation complete. All transcript/chapter pairs are valid!")

if __name__ == "__main__":
    validate_all_transcripts_and_chapters()
