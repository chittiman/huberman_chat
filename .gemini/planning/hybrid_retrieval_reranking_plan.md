# Hybrid Search and Reranking Strategy Plan

This document outlines two proposed hybrid retrieval strategies for the Huberman Chat project. The goal is to benchmark these options to find the optimal balance between retrieval accuracy and performance.

## Overview

Both proposed options follow a two-stage process:
1.  **Retrieval:** Fetch an initial set of candidate documents using two parallel methods: keyword search and vector search.
2.  **Reranking:** Refine the initial results using a fusion or reranking model to produce the final, more accurate list.

---

### Option 1: Retrieval + Reciprocal Rank Fusion (RRF)

-   **Strategy:** Combine the ranked lists from the keyword and vector searches using the Reciprocal Rank Fusion (RRF) algorithm. RRF calculates a new score for each document based on its rank in the input lists, effectively boosting documents that appear high on either or both lists.

-   **Pros:**
    -   **Extremely Fast:** The calculation is simple and adds negligible latency.
    -   **Simple Implementation:** Requires only a few lines of code.
    -   **No Extra Models:** Avoids the overhead of loading and running another large model.
    -   **Strong Baseline:** A well-regarded and effective fusion method.

-   **Cons:**
    -   **Superficial:** RRF only considers the *rank* of the results, not their content. It cannot deeply re-evaluate the relevance of the documents against the query.

---

### Option 2: Retrieval + ColBERT-style Dense Reranker

-   **Strategy:** Take the top `k` candidate documents from the initial retrieval stage and pass them to a powerful, ColBERT-style reranking model. This model performs a fine-grained analysis by comparing the query's tokens against the document's tokens to compute a highly accurate relevance score.

-   **Pros:**
    -   **State-of-the-Art Accuracy:** Capable of understanding complex contextual nuances, leading to superior precision.
    -   **Deep Understanding:** Re-examines the documents in the context of the query for a more accurate final ranking.

-   **Cons:**
    -   **High Computational Cost:** Adds significant latency and requires more powerful hardware (potentially a GPU).
    -   **Complex Implementation:** Involves integrating and managing another large neural network.

---

## Benchmarking Plan

To make an informed decision, we will implement both options and evaluate them on quality and performance.

**Phase 1: Build the Foundation (Common to Both Options)**
1.  **Implement Keyword Search:** Create a function that takes a query and returns a ranked list of `(chapter_id, score)` using a classic algorithm like BM25.
2.  **Implement Vector Search:** Create a function that takes a query, embeds it, and returns a ranked list of `(chapter_id, score)` from the ChromaDB vector store.

**Phase 2: Implement the Rerankers**
3.  **Implement RRF:** Create a function that takes the two lists from Phase 1 and applies the RRF formula.
4.  **Implement ColBERT Reranker:** Select a pre-trained ColBERT model and create a function to re-score the top `k` candidates from the initial retrieval.

**Phase 3: Execute the Benchmark**
5.  **Evaluation Dataset:** Use the question-answer pairs in `data/questions/` as the ground truth. The `ground_truth_reference` field will be used to identify correct chapters.
6.  **Evaluation Metrics:**
    -   **Mean Reciprocal Rank (MRR):** Measures the rank of the first correct result.
    -   **Precision@K:** Measures the percentage of correct results in the top K.
    -   **Average Latency:** Measures the time taken per query.
7.  **Run the Test:**
    -   For each question in the evaluation set, run the full pipeline for both Option 1 and Option 2.
    -   Record the metrics for each run.
    -   Compare the aggregated results to decide which option provides the best trade-off for our needs.
