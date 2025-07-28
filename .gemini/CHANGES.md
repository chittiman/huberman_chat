# Changelog

This file tracks significant changes made to the `huberman_chat` codebase.

## Session: 2025-07-28

### 4. Simplified Pydantic Schema to Resolve API Errors

-   **Files Modified:**
    -   `pydantic_models.py`

-   **Description of Changes:**
    -   Removed granular validation constraints (`min_length`, `max_length`, `min_items`, `max_items`) from the `RAGQuestion` and `RAGQuestionSet` Pydantic models.

-   **Reason for Change:**
    -   The question generation script was failing with a `400 INVALID_ARGUMENT` error from the Gemini API. The error message indicated that the Pydantic schema was too complex and restrictive. Simplifying the schema by removing these constraints resolves the API error while still enforcing the core data structure.

## Session: 2025-07-27

### 3. Refactored Application Logging

-   **Files Modified:**
    -   `yt_chapters_extraction.py`
    -   `question_generation.py`
    -   `chapter_timestamp_validators.py`
    -   `logging_config.py` (new file)

-   **Description of Changes:**
    -   Created a new `logging_config.py` module to provide a centralized and consistent logging setup for the entire application.
    -   Replaced all `print()` statements in the main processing scripts with structured logging calls (e.g., `logger.info()`, `logger.warning()`, `logger.error()`).
    -   Each script now initializes the logger using the central configuration, directing output to both the console and a dedicated log file (e.g., `validation.log`).
    -   Enhanced error logging to include stack traces (`exc_info=True`), which will make debugging significantly easier.

-   **Reason for Change:**
    -   The previous logging was inconsistent and relied on basic `print()` calls, making it difficult to control verbosity or trace errors effectively.
    -   This new system introduces standardized log levels, consistent formatting, and flexible output (to both console and file), which are best practices for application development. It provides clearer, more actionable feedback during script execution.

### 2. Enhanced Data Model for Questions & Chapters

-   **Files Modified:**
    -   `pydantic_models.py`
    -   `prompts/question_creation_prompts/system_prompt.md`
    -   `prompts/question_creation_prompts/user_prompt.md`

-   **Description of Changes:**
    -   Updated the `RAGQuestion` Pydantic model to include a new `question_id: int` field. This provides a unique, stable identifier for each generated question.
    -   Modified the `ground_truth_reference` field in the `RAGQuestion` model from `List[str]` to `List[int]`. This allows questions to reference the specific `chapter_id` of the source chapters, creating a more robust relational link between questions and the content they are based on.
    -   Updated the system and user prompts for question generation to instruct the AI model to generate these new fields correctly.

-   **Reason for Change:**
    -   To improve the data structure by creating a clear, machine-readable link between generated questions and the specific chapter(s) they reference. This is crucial for evaluating the RAG system's retrieval accuracy and for better data traceability.

### 1. Improved Project Documentation

-   **Files Modified:**
    -   `README.md`
    -   `CODEBASE_ANALYSIS.md` (new file)

-   **Description of Changes:**
    -   Created `CODEBASE_ANALYSIS.md` to provide a detailed breakdown of the project's architecture, data pipeline, and key components.
    -   Significantly expanded the `README.md` to include a detailed project description, core features, a workflow overview, setup and installation instructions, and usage guidelines.

-   **Reason for Change:**
    -   To make the project more accessible and understandable for developers (including ourselves). The previous `README.md` was too brief, and a dedicated analysis document provides a deeper technical overview.