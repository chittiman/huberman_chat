#data/chapters has <video_id>.json files
#"chapters" key in the output is a list of chapter objects
#I have to add "chapter_id" to each chapter object
#It should be the first key in the chapter object
#Store the updated chapter objects in the same file
#Write a function for ach file
#in if __name__ == "__main__": block run the loop for all files in data/chapters
#Use pathlib read_text and write_text for file operations
import json
from pathlib import Path
from tqdm import tqdm

def add_chapter_ids_to_file(file_path: Path):
    """Add chapter_id to each chapter object in the given JSON file."""
    if not file_path.exists():
        print(f"File {file_path} does not exist.")
        return

    data = json.loads(file_path.read_text(encoding='utf-8'))

    # Check if 'chapters' key exists
    if 'chapters' not in data:
        print(f"No 'chapters' key found in {file_path}.")
        return

    chapters = data['chapters']
    
    # Add chapter_id to each chapter object
    # Ensure chapter_id is the first key in each chapter object
    modified_chapters = []
    for idx, chapter in enumerate(chapters):
        chapter['chapter_id'] = idx + 1  # Start IDs from 1
        # Ensure chapter_id is the first key
        chapter = {'chapter_id': chapter['chapter_id'], **chapter}
        modified_chapters.append(chapter)
    data['chapters'] = modified_chapters
    video_id = file_path.stem.split('.')[0]
    data = {'video_id': video_id, **data}

    file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

if __name__ == "__main__":
    cur_dir = Path.cwd()
    data_dir = cur_dir / "data"
    chapters_dir = data_dir / "chapters"

    # Ensure chapters directory exists
    chapters_dir.mkdir(parents=True, exist_ok=True)

    # Process each JSON file in the chapters directory
    json_files = list(chapters_dir.glob("*.json"))
    if not json_files:
        print("No JSON files found in data/chapters.")
    else:
        for json_file in tqdm(json_files, desc="Adding chapter IDs"):
            add_chapter_ids_to_file(json_file)
