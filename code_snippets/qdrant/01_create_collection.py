
import os
from qdrant_client import QdrantClient, models

# --- Configuration ---
QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")
COLLECTION_NAME = "huberman_labs_hybrid_search"


def create_hybrid_collection(client: QdrantClient, collection_name: str):
    """
    Creates a Qdrant collection configured for hybrid search with dense,
    sparse, and late-interaction (ColBERT) vectors, based on the project's
    planning documents.

    Args:
        client: An initialized QdrantClient instance.
        collection_name: The name of the collection to create.
    """
    try:
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config={
                # Dense vectors for semantic search (e.g., all-MiniLM-L6-v2)
                "dense": models.VectorParams(
                    size=384,
                    distance=models.Distance.COSINE,
                ),
                # Late-interaction vectors for reranking (e.g., ColBERT)
                "colbert": models.VectorParams(
                    size=128,  # Size for colbertv2.0
                    distance=models.Distance.COSINE,
                    multivector_config=models.MultiVectorConfig(
                        comparator=models.MultiVectorComparator.MAX_SIM,
                    ),
                    hnsw_config=models.HnswConfigDiff(m=0)  # Disable HNSW for reranking
                ),
            },
            # Sparse vectors for keyword-based search (e.g., BM25)
            sparse_vectors_config={
                "sparse": models.SparseVectorParams(
                    modifier=models.Modifier.IDF
                )
            }
        )
        print(f"Successfully created collection: '{collection_name}'")
        collection_info = client.get_collection(collection_name=collection_name)
        print("Collection configuration:")
        print(collection_info)

    except Exception as e:
        print(f"An error occurred while creating the collection: {e}")


def main():
    """Main function to connect to Qdrant and create the collection."""
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    print(f"Connecting to Qdrant at: {QDRANT_URL}")
    create_hybrid_collection(client, COLLECTION_NAME)


if __name__ == "__main__":
    main()
