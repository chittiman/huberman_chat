# Changelog

This file tracks significant changes made to the `huberman_chat` codebase.

## Session: 2025-08-01

### 1. Reset Qdrant Implementation for Major Version Upgrade

-   **Files Modified:**
    -   `create_qdrant_index.py` (emptied)
    -   `tests/test_create_qdrant_index.py` (emptied)
    -   `.gemini/CODEBASE_ANALYSIS.md`
-   **Files Added:**
    -   `code_snippets/fast_embed/fastembed_examples.py` (Marimo notebook)
    -   `code_snippets/qdrant/qdrant_examples.py` (Marimo notebook)
-   **Files Deleted:**
    -   Old Python script code snippets for Qdrant.
-   **Description of Changes:**
    -   Due to a major version upgrade in the Qdrant library, the existing indexing script and its corresponding test became obsolete. Both `create_qdrant_index.py` and `tests/test_create_qdrant_index.py` have been cleared to allow for a fresh start.
    -   The old, outdated code snippets for Qdrant were deleted.
    -   New, up-to-date code examples for `fastembed` and the new version of `qdrant` have been added as interactive Marimo notebooks in the `code_snippets/` directory. These will serve as a reference for the new implementation.
    -   The `CODEBASE_ANALYSIS.md` file was updated to reflect this reset and the new reference-based approach.
-   **Reason for Change:**
    -   To address breaking changes from a Qdrant major version upgrade and to ensure the project is ready for a new implementation based on the latest, correct code examples.

## Session: 2025-07-30

### 1. Disabled HNSW for ColBERT Vectors in Qdrant Collection

-   **Files Modified:**
    -   `code_snippets/qdrant/01_create_collection.py`
-   **Description of Changes:**
    -   Added `hnsw_config=models.HnswConfigDiff(m=0)` to the `colbert` vector configuration in `01_create_collection.py`.
    -   Included a comment `# Disable HNSW for reranking` to clarify the purpose.
-   **Reason for Change:**
    -   HNSW is not required for late-interaction (ColBERT) vectors, as they are primarily used for reranking where maximum similarity is determined directly, not through approximate nearest neighbor search. Disabling HNSW optimizes resource usage and performance for this specific vector type.

## Session: 2025-07-29

### 1. Corrected Pydantic Data Models

-   **Files Modified:**
    -   `pydantic_models.py`
-   **Description of Changes:**
    -   Added the `video_id: str` field to the `VideoAnalysis` Pydantic model.
    -   Added the `chapter_id: int` field to the `Chapter` Pydantic model.
-   **Reason for Change:**
    -   The existing models did not accurately reflect the structure of the JSON data, causing `ValidationError` and `AttributeError` failures in the test suite. These changes align the models with the data, ensuring proper validation and fixing the tests.

## Session: 2025-07-28 (End of Day)

### 6. Began Qdrant Indexing Script with TDD

-   **Files Added:**
    -   `create_qdrant_index.py`
    -   `tests/test_create_qdrant_index.py`
-   **Description of Changes:**
    -   Created the initial scaffolding for the Qdrant indexing script.
    -   Implemented and unit-tested the first two helper functions, `prepare_chapter_document` and `load_chapter_data`, following a test-driven development (TDD) approach.
-   **Reason for Change:**
    -   To begin the implementation of the core indexing logic required for our new Qdrant-based hybrid search strategy, ensuring code quality and correctness from the start with unit tests.

### 5. Established Testing Framework

-   **Files Modified:**
    -   `pyproject.toml`
    -   `uv.lock`
-   **Files Added:**
    -   `tests/`
-   **Description of Changes:**
    -   Added `pytest` and `pytest-mock` as development dependencies to the project.
    -   Created the `tests` directory to house all future test files.
-   **Reason for Change:**
    -   To formally establish a testing framework, enabling a robust, test-driven development process which improves code reliability and simplifies debugging.

---
*Previous entries below this line.*
---

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