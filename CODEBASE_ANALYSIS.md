# Codebase Analysis

This document outlines the structure and workflow of the `huberman_chat` project.

## Project Overview

The project is designed to create a chatbot based on the content of Huberman Labs videos. It processes video transcripts to extract chapters, generate questions, and create a structured dataset for a RAG (Retrieval-Augmented Generation) system.

## Data Pipeline

The project follows a clear data pipeline:

1.  **Subtitle Ingestion**: Raw video subtitles are stored as `.srt` files in the `data/subtitles/` directory. These are the primary input for the system.

2.  **Chapter Extraction**: The `yt_chapters_extraction.py` script reads the `.srt` files, uses the `GeminiChat` class (from `gemini_chat_completion.py`) to interact with a Gemini model, and extracts a summary and distinct chapters from the transcript. The output is a JSON file for each video, saved in `data/chapters/`, with its structure defined by the `VideoAnalysis` Pydantic model.

3.  **Chapter ID Enrichment**: The `add_chapter_ids.py` script processes the JSON files in `data/chapters/`, adding a unique `chapter_id` to each chapter and a `video_id` to the top-level object. This enriches the data for easier referencing.

4.  **Question Generation**: The `question_generation.py` script takes the chapter-enriched JSON files as input. It uses the `GeminiChat` class again, this time with different prompts, to generate a set of questions based on the video's content. The output is a new set of JSON files stored in `data/questions/`, structured according to the `RAGQuestionSet` Pydantic model.

5.  **Timestamp Validation**: The `chapter_timestamp_validators.py` script serves as a data quality assurance tool. It compares the timestamps in the generated chapter files against the original `.srt` transcripts to ensure they are valid and within the video's duration, logging any discrepancies.

## Key Files and Components

-   **`main.py`**: The main entry point of the application. Currently, it is a placeholder and does not contain any significant logic.

-   **`gemini_chat_completion.py`**: A core component that provides the `GeminiChat` class. This class is a reusable wrapper around the Google Gemini API, handling prompt loading, API calls (with retries), and parsing of both text and structured (Pydantic model) outputs.

-   **`pydantic_models.py`**: Defines the data structures used throughout the project. Key models include:
    -   `VideoAnalysis`: For the output of the chapter extraction process.
    -   `Chapter`: A sub-model for individual chapters.
    -   `RAGQuestionSet`: For the output of the question generation process.
    -   `RAGQuestion`: A sub-model for individual questions.

-   **`yt_chapters_extraction.py`**: The first major script in the data pipeline. It orchestrates the process of reading transcripts and generating chapter summaries.

-   **`add_chapter_ids.py`**: A utility script for data enrichment, adding necessary identifiers to the chapter files.

-   **`question_generation.py`**: The second major script in the pipeline, responsible for creating question-answer pairs for the RAG system.

-   **`chapter_timestamp_validators.py`**: A utility script for ensuring the integrity and quality of the generated chapter data.

-   **`prompts/`**: This directory contains the prompt templates (system and user) for the Gemini models, separating the model instructions from the application logic.

-   **`data/`**: This directory is the central hub for all data, separated into subdirectories for each stage of the pipeline (subtitles, chapters, questions).
