# Qdrant Hybrid Search & Reranking Code Examples

This file contains key code snippets extracted from Qdrant's documentation, serving as a reference for implementing our hybrid search pipeline.

*   **Source 1:** [Reranking in Hybrid Search](https://qdrant.tech/documentation/advanced-tutorials/reranking-hybrid-search/)
*   **Source 2:** [Hybrid Search Revamped](https://qdrant.tech/articles/hybrid-search/)

---

### 1. Initial Setup & Loading Models

This code installs `fastembed` and shows how to load the three different types of embedding models we need: dense, sparse, and late-interaction (ColBERT).

```python
# pip install fastembed

from fastembed import TextEmbedding, LateInteractionTextEmbedding, SparseTextEmbedding

# Load the embedding models
dense_embedding_model = TextEmbedding("sentence-transformers/all-MiniLM-L6-v2")
bm25_embedding_model = SparseTextEmbedding("Qdrant/bm25")
late_interaction_embedding_model = LateInteractionTextEmbedding("colbert-ir/colbertv2.0")
```

### 2. Creating a Qdrant Collection for Hybrid Search

This code creates a new collection in Qdrant configured to handle multiple vector types. Note the use of `multivector_config` for the ColBERT model and the `sparse_vectors_config`.

```python
from qdrant_client import QdrantClient, models

client = QdrantClient("http://localhost:6333")

# Create a collection for hybrid search
client.create_collection(
    collection_name="hybrid-search-collection",
    vectors_config={
        "dense": models.VectorParams(
            size=384, # From all-MiniLM-L6-v2
            distance=models.Distance.COSINE,
        ),
        "colbert": models.VectorParams(
            size=128, # From colbertv2.0
            distance=models.Distance.COSINE,
            multivector_config=models.MultiVectorConfig(
                comparator=models.MultiVectorComparator.MAX_SIM,
            ),
        ),
    },
    sparse_vectors_config={
        "sparse": models.SparseVectorParams(modifier=models.Modifier.IDF)
    }
)
```

### 3. Indexing Multiple Vectors

This section shows how to "upsert" (insert or update) documents with their dense, sparse, and late-interaction embeddings into the Qdrant collection.

```python
from qdrant_client.models import PointStruct

# Assume 'documents' is a list of strings
# Assume the embedding models from Step 1 are loaded

dense_embeddings = list(dense_embedding_model.embed(documents))
sparse_embeddings = list(bm25_embedding_model.embed(documents))
late_interaction_embeddings = list(late_interaction_embedding_model.embed(documents))

points = []
for idx, (doc, dense_emb, sparse_emb, colbert_emb) in enumerate(zip(documents, dense_embeddings, sparse_embeddings, late_interaction_embeddings)):
    point = PointStruct(
        id=idx,
        vector={
            "dense": dense_emb,
            "sparse": sparse_emb.as_object(),
            "colbert": colbert_emb,
        },
        payload={"document": doc}
    )
    points.append(point)

operation_info = client.upsert(
    collection_name="hybrid-search-collection",
    points=points,
    wait=True
)
```

### 4. Performing Hybrid Search with Reranking

This code demonstrates the final query. It uses the `prefetch` parameter to run the initial dense and sparse searches, then uses the main `query` with the ColBERT vectors to rerank the results.

```python
query = "What is feature scaling?"

# Generate embeddings for the query
dense_vector = next(dense_embedding_model.query_embed(query))
sparse_vector = next(bm25_embedding_model.query_embed(query))
colbert_vector = next(late_interaction_embedding_model.query_embed(query))

# Define prefetch queries for the initial retrieval
prefetch = [
    models.Prefetch(
        query=dense_vector,
        using="dense",
        limit=20,
    ),
    models.Prefetch(
        query=models.SparseVector(**sparse_vector.as_object()),
        using="sparse",
        limit=20,
    ),
]

# Perform the final query with reranking
results = client.query_points(
    collection_name="hybrid-search-collection",
    prefetch=prefetch,
    query=colbert_vector,
    using="colbert",
    with_payload=True,
    limit=10,
)

# Print the results
for result in results:
    print(f"Score: {result.score}, Document: {result.payload['document']}")

```
