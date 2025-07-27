import os
from pathlib import Path
import json
import re
from datetime import datetime, timedelta

def parse_srt_timestamp(timestamp_str):
    """Parse SRT timestamp format (HH:MM:SS,mmm) to total seconds"""
    # Remove the arrow part if present
    timestamp_str = timestamp_str.split(' --> ')[0].strip()
    
    # Parse HH:MM:SS,mmm format
    time_part, ms_part = timestamp_str.split(',')
    hours, minutes, seconds = map(int, time_part.split(':'))
    milliseconds = int(ms_part)
    
    total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
    return total_seconds

def parse_chapter_timestamp(timestamp_str):
    """Parse chapter timestamp format (M:SS or MM:SS) to total seconds"""
    # Remove any extra characters and split by ':'
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
    # Find all timestamp lines in the transcript
    timestamp_pattern = r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}'
    timestamps = re.findall(timestamp_pattern, transcript_content)
    
    if not timestamps:
        raise ValueError("No timestamps found in transcript")
    
    # Get the last timestamp's end time
    last_timestamp = timestamps[-1]
    end_time = last_timestamp.split(' --> ')[1]
    
    return parse_srt_timestamp(end_time)

def validate_timestamps(transcript_file, chapters_file):
    """Main function to validate timestamps"""
    try:
        # Read transcript file
        with open(transcript_file, 'r', encoding='utf-8') as f:
            transcript_content = f.read()
        
        # Read chapters JSON file
        with open(chapters_file, 'r', encoding='utf-8') as f:
            chapters_data = json.load(f)
        
        # Get final timestamp from transcript
        final_transcript_seconds = get_final_transcript_timestamp(transcript_content)
        final_transcript_time = str(timedelta(seconds=int(final_transcript_seconds)))
        
        print(f"Final transcript timestamp: {final_transcript_time} ({final_transcript_seconds:.3f} seconds)")
        print("-" * 60)
        
        # Validate each chapter timestamp
        valid_timestamps = []
        invalid_timestamps = []
        
        for i, chapter in enumerate(chapters_data.get('chapters', [])):
            timestamp = chapter.get('timestamp', '')
            heading = chapter.get('heading', f'Chapter {i+1}')
            
            try:
                chapter_seconds = parse_chapter_timestamp(timestamp)
                
                if chapter_seconds <= final_transcript_seconds:
                    valid_timestamps.append({
                        'timestamp': timestamp,
                        'seconds': chapter_seconds,
                        'heading': heading,
                        'status': 'VALID'
                    })
                    print(f"✓ {timestamp} ({chapter_seconds:.1f}s) - {heading}")
                else:
                    invalid_timestamps.append({
                        'timestamp': timestamp,
                        'seconds': chapter_seconds,
                        'heading': heading,
                        'status': 'INVALID - EXCEEDS TRANSCRIPT'
                    })
                    print(f"✗ {timestamp} ({chapter_seconds:.1f}s) - {heading} [EXCEEDS TRANSCRIPT]")
                    
            except ValueError as e:
                invalid_timestamps.append({
                    'timestamp': timestamp,
                    'seconds': None,
                    'heading': heading,
                    'status': f'INVALID - PARSE ERROR: {e}'
                })
                print(f"✗ {timestamp} - {heading} [PARSE ERROR: {e}]")
        
        # Summary
        print("-" * 60)
        print(f"VALIDATION SUMMARY:")
        print(f"Total chapters: {len(chapters_data.get('chapters', []))}")
        print(f"Valid timestamps: {len(valid_timestamps)}")
        print(f"Invalid timestamps: {len(invalid_timestamps)}")
        
        if invalid_timestamps:
            print(f"\nINVALID TIMESTAMPS:{chapters_file}")
            for item in invalid_timestamps:
                print(f"  - {item['timestamp']} ({item['heading']}): {item['status']}")
            return False
        else:
            print(f"\n✓ All timestamps are valid and within transcript bounds!")
            return True
            
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# Example usage with sample data
def test_with_sample_data():
    """Test function using the provided sample data"""
    
    # Sample transcript content
    transcript_content = """90
00:03:37,296 --> 00:03:38,700
It's a common phenotype.

91
00:03:38,700 --> 00:03:41,040
Like we've studied it,
and maybe 50% of people

92
00:03:41,040 --> 00:03:42,840
with obesity have that."""
    
    # Sample chapters data
    chapters_data = {
        "overall_summary": "The video discusses the growing use of nicotine products...",
        "chapters": [
            {
                "timestamp": "0:00",
                "heading": "Nicotine Use Trends and Perceptions",
                "content": "There is an increased use of various nicotine products..."
            },
            {
                "timestamp": "0:36",
                "heading": "Nicotine's Impact on ADHD and Executive Functions", 
                "content": "The discussion focuses on how nicotine affects individuals..."
            },
            {
                "timestamp": "1:31",
                "heading": "Unique Properties of Nicotine as a Stimulant",
                "content": "Nicotine is described as unique among stimulants..."
            }
        ]
    }
    
    # Write sample files for testing
    with open('sample_transcript.srt', 'w', encoding='utf-8') as f:
        f.write(transcript_content)
    
    with open('sample_chapters.json', 'w', encoding='utf-8') as f:
        json.dump(chapters_data, f, indent=2)
    
    print("Testing with sample data:")
    print("=" * 60)
    
    # Run validation
    result = validate_timestamps('sample_transcript.srt', 'sample_chapters.json')
    
    # Clean up sample files
    import os
    try:
        os.remove('sample_transcript.srt')
        os.remove('sample_chapters.json')
    except:
        pass
    
    return result


def validate_all_transcripts_and_chapters():
    """
    Validate all transcript/chapter pairs in data/subtitles and data/chapters.
    Log mistakes to mistakes.txt.
    """
    subtitles_dir = Path("data/subtitles")
    chapters_dir = Path("data/chapters")
    mistakes_path = Path("mistakes.txt")
    mistakes = []

    for srt_file in subtitles_dir.glob("*.srt"):
        json_file = chapters_dir / (srt_file.stem + ".json")
        if not json_file.exists():
            mistakes.append(f"Missing chapters file for {srt_file.name}")
            continue
        result = validate_timestamps(str(srt_file), str(json_file))
        if not result:
            mistakes.append(f"{srt_file.name}")

    if mistakes:
        with open(mistakes_path, "w", encoding="utf-8") as f:
            for line in mistakes:
                f.write(line + "\n")
        print(f"Mistakes logged to {mistakes_path}")
    else:
        pass
        # print("All transcript/chapter pairs are valid!")

if __name__ == "__main__":
    validate_all_transcripts_and_chapters()