# tests/test_create_qdrant_index.py
import sys
from pathlib import Path
import pytest
import json

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from create_qdrant_index import prepare_chapter_document, load_chapter_data
from pydantic_models import VideoAnalysis


def test_prepare_chapter_document():
    """
    Tests that the chapter document is prepared correctly by combining
    heading and content into a single string.
    """
    # Arrange: Create a sample chapter dictionary
    sample_chapter = {
        "heading": "The Role of Sunlight",
        "content": "Sunlight exposure in the morning is crucial for setting the circadian rhythm.",
        "chapter_id": 1,
        "timestamp": "10:30"
    }

    # Act: Call the function under test
    document = prepare_chapter_document(sample_chapter)

    # Assert: Check if the output is as expected
    expected_document = "Heading: The Role of Sunlight\nContent: Sunlight exposure in the morning is crucial for setting the circadian rhythm."
    assert document == expected_document

def test_prepare_chapter_document_with_empty_content():
    """
    Tests the function's behavior with an empty content field.
    """
    # Arrange
    sample_chapter = {
        "heading": "Empty Content Test",
        "content": "",
    }

    # Act
    document = prepare_chapter_document(sample_chapter)

    # Assert
    expected_document = "Heading: Empty Content Test\nContent: "
    assert document == expected_document

def test_load_chapter_data(tmp_path):
    """
    Tests that chapter data is loaded correctly from a JSON file
    and parsed into a VideoAnalysis Pydantic model.
    """
    # Arrange: Create a temporary JSON file with sample data
    sample_data = {
        "video_id": "test_video_123",
        "overall_summary": "A test summary.",
        "chapters": [
            {"chapter_id": 1, "heading": "Intro", "content": "Content 1"},
            {"chapter_id": 2, "heading": "Main", "content": "Content 2"}
        ],
        "topics": ["testing", "pydantic"]
    }
    file_path = tmp_path / "test_data.json"
    with open(file_path, "w") as f:
        json.dump(sample_data, f)

    # Act: Call the function under test
    video_analysis = load_chapter_data(file_path)

    # Assert: Check that the output is a valid VideoAnalysis object
    # and that its content matches the sample data.
    assert isinstance(video_analysis, VideoAnalysis)
    assert video_analysis.video_id == "test_video_123"
    assert len(video_analysis.chapters) == 2
    assert video_analysis.chapters[1].heading == "Main"
