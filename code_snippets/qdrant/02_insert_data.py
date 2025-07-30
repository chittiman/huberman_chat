
import os
from qdrant_client import QdrantClient, models

# --- Configuration ---
QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")
COLLECTION_NAME = "huberman_labs_hybrid_search"

def insert_chapter_data(client: QdrantClient, collection_name: str):
    """
    Inserts dummy chapter data into the Qdrant collection.
    In a real scenario, this would involve processing actual chapter data
    and generating embeddings.
    """
    try:
        # Dummy data for demonstration
        points = [
            models.PointStruct(
                id=1,
                vector={
                    "dense": [0.1, 0.2, 0.3, 0.4] * 96, # Dummy dense vector (size 384)
                    "colbert": [0.5, 0.6, 0.7, 0.8] * 32, # Dummy colbert vector (size 128)
                    "sparse": models.SparseVector(
                        indices=[10, 20, 30],
                        values=[0.1, 0.2, 0.3]
                    )
                },
                payload={
                    "video_id": "video123",
                    "chapter_id": 1,
                    "title": "Introduction to Neuroscience",
                    "timestamp": "00:00:00",
                    "content": "This chapter introduces the basics of neuroscience and brain function."
                }
            ),
            models.PointStruct(
                id=2,
                vector={
                    "dense": [0.9, 0.8, 0.7, 0.6] * 96, # Dummy dense vector (size 384)
                    "colbert": [0.4, 0.3, 0.2, 0.1] * 32, # Dummy colbert vector (size 128)
                    "sparse": models.SparseVector(
                        indices=[15, 25, 35],
                        values=[0.4, 0.5, 0.6]
                    )
                },
                payload={
                    "video_id": "video123",
                    "chapter_id": 2,
                    "title": "Sleep and its Importance",
                    "timestamp": "00:15:30",
                    "content": "Understanding the critical role of sleep in cognitive function and health."
                }
            )
        ]

        operation_info = client.upsert(
            collection_name=collection_name,
            wait=True,
            points=points
        )
        print(f"Successfully inserted data: {operation_info}")

    except Exception as e:
        print(f"An error occurred while inserting data: {e}")

def main():
    """Main function to connect to Qdrant and insert data."""
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
    print(f"Connecting to Qdrant at: {QDRANT_URL}")
    insert_chapter_data(client, COLLECTION_NAME)

if __name__ == "__main__":
    main()
