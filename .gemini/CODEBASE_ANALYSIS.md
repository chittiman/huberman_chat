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

## Retrieval Strategy: Qdrant-Native Hybrid Search

To retrieve relevant context for user queries, the project will leverage a sophisticated hybrid search system built directly within Qdrant. This server-side approach is chosen for its performance and simplicity.

The implementation will be housed in `create_qdrant_index.py`, which is currently empty and will be developed using the latest library versions.

Updated code examples for `fastembed` and `qdrant` (v2.x) are available as interactive Marimo notebooks in the `code_snippets/` directory for reference. These demonstrate the multi-vector and hybrid search capabilities that will be implemented.

The planned approach involves:

1.  **Indexing**:
    *   **Multi-Vector Model**: Each chapter document will be indexed using multiple vector embeddings (dense, sparse, and late-interaction) to enable a multi-faceted search.
    *   **Data Upload**: The `fastembed` library will be used to generate these embeddings, which will then be uploaded to a single Qdrant collection configured for hybrid search.

2.  **Querying**:
    *   User queries will be transformed into the same multiple vector types.
    *   A single query will be sent to Qdrant's API to perform a two-stage search:
        1.  **Prefetch**: A parallel search using dense and sparse vectors to retrieve a broad set of initial candidates.
        2.  **Rerank**: The late-interaction model will be used to re-score and re-order the candidate set for high accuracy.

This method offloads all complex search and fusion logic to the optimized Qdrant server, resulting in a cleaner and more performant retrieval system.

## Key Files and Components

-   **`main.py`**: The main entry point of the application. Currently, it is a placeholder and does not contain any significant logic.

-   **`gemini_chat_completion.py`**: A core component that provides the `GeminiChat` class. This is a reusable wrapper around the Google Gemini API, handling prompt loading, API calls (with retries), and parsing of both text and structured (Pydantic model) outputs.

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

