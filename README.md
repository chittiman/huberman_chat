# Huberman Chat

This project is a data processing pipeline designed to build a structured dataset from Huberman Labs video transcripts. The ultimate goal is to create a high-quality dataset suitable for training and evaluating a Retrieval-Augmented Generation (RAG) system that can answer questions based on the video content.

## Core Features

-   **Chapter Extraction**: Automatically extracts structured summaries and chapters from raw `.srt` video transcripts.
-   **Data Enrichment**: Enriches the extracted data by adding unique `video_id` and `chapter_id` identifiers for precise referencing.
-   **Question Generation**: Generates a diverse set of questions based on the video content, complete with metadata like answer type, difficulty, and context requirements.
-   **Timestamp Validation**: Includes a utility to validate the accuracy of chapter timestamps against the original transcripts, ensuring data quality.

## Workflow Overview

The project follows a sequential data pipeline:

1.  **Input**: Place raw `.srt` transcript files into the `data/subtitles/` directory.
2.  **Chapter Extraction**: Run `yt_chapters_extraction.py` to process the transcripts. This script uses a Gemini model to generate a summary and a list of chapters for each video, saving the output as a JSON file in `data/chapters/`.
3.  **ID Enrichment**: Run `add_chapter_ids.py` to add unique `video_id` and `chapter_id` fields to each chapter file in `data/chapters/`.
4.  **Question Generation**: Run `question_generation.py` to generate question sets from the chapter files. The output is saved as JSON files in `data/questions/`.
5.  **Validation**: (Optional) Run `chapter_timestamp_validators.py` to check for any timestamp inconsistencies in the generated chapter files.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd huberman_chat
    ```

2.  **Install dependencies:**
    This project uses `uv` for package management.
    ```bash
    uv pip install -r requirements.txt
    ```
    *(Note: If you do not have a `requirements.txt`, you will need to generate one from `pyproject.toml` or install dependencies directly from it.)*

3.  **Set up environment variables:**
    Create a `.env` file in the project root and add your Gemini API key:
    ```
    GEMINI_API_KEY="your_api_key_here"
    ```

## Usage

To run the full data pipeline, execute the scripts in the following order:

1.  **Extract Chapters:**
    ```bash
    python yt_chapters_extraction.py
    ```

2.  **Add Chapter IDs:**
    ```bash
    python add_chapter_ids.py
    ```

3.  **Generate Questions:**
    ```bash
    python question_generation.py
    ```

4.  **Validate Timestamps (Optional):**
    ```bash
    python chapter_timestamp_validators.py
    ```

## Project Structure

-   `data/`: Contains all data, organized by processing stage.
    -   `subtitles/`: Raw `.srt` transcript files.
    -   `chapters/`: JSON files with extracted chapters.
    -   `questions/`: JSON files with generated question sets.
-   `prompts/`: Stores the system and user prompt templates for interacting with the Gemini model.
-   `*.py`: Python scripts that drive the data processing pipeline.