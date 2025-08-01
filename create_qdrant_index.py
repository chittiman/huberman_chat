
import json
from pathlib import Path

from fastembed import LateInteractionTextEmbedding, SparseTextEmbedding, TextEmbedding
from loguru import logger
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import PointStruct
from uuid import uuid4

from pydantic_models import VideoAnalysis

# 1. Define constants for model names and the Qdrant collection
DENSE_MODEL = "jinaai/jina-embeddings-v2-base-en"
SPARSE_MODEL = "Qdrant/bm25"
LATE_INTERACTION_MODEL = "jinaai/jina-colbert-v2"
COLLECTION_NAME = "huberman_clips"


# 2. Initialize embedding models and Qdrant client
logger.info("Initializing embedding models and Qdrant client...")
dense_embed_model = TextEmbedding(model_name=DENSE_MODEL)
sparse_embed_model = SparseTextEmbedding(model_name=SPARSE_MODEL)
late_embed_model = LateInteractionTextEmbedding(model_name=LATE_INTERACTION_MODEL)
client = QdrantClient(url="http://localhost:6333")
logger.info("Initialization complete.")


def get_json_files(data_path: Path):
    """Generator to yield all json files in a directory."""
    return data_path.rglob("*.json")


def create_index():
    """
    Creates a Qdrant index for the Huberman Labs chapters using a hybrid
    approach with dense, sparse, and late-interaction vectors.
    """
    # 3. Get vector sizes dynamically from the embedding models
    dense_vector_size = len(next(dense_embed_model.embed("test"))) # type: ignore
    late_interaction_vector_size = next(late_embed_model.embed("test")).shape[1] # type: ignore

    # 4. Check if the collection already exists
    try:
        if client.collection_exists(collection_name=COLLECTION_NAME):
            logger.info(f"Collection '{COLLECTION_NAME}' already exists. Skipping creation.")
        else:
            # 5. Create the Qdrant collection if it doesn't exist
            logger.info(f"Collection '{COLLECTION_NAME}' does not exist. Creating...")
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config={
                    DENSE_MODEL: models.VectorParams(
                        size=dense_vector_size,
                        distance=models.Distance.COSINE,
                    ),
                    LATE_INTERACTION_MODEL: models.VectorParams(
                        size=late_interaction_vector_size,
                        distance=models.Distance.COSINE,
                        multivector_config=models.MultiVectorConfig(
                            comparator=models.MultiVectorComparator.MAX_SIM,
                        ),
                        hnsw_config=models.HnswConfigDiff(m=0),  # Disable HNSW for reranking
                    ),
                },
                sparse_vectors_config={
                    SPARSE_MODEL: models.SparseVectorParams(modifier=models.Modifier.IDF)
                },
            )
            logger.info("Collection created successfully.")
    except Exception as e:
        logger.error(f"Could not check or create collection: {e}", exc_info=True)
        return

    # 6. Get all json files from the chapters directory
    chapters_path = Path("data/chapters")
    json_files = list(get_json_files(chapters_path))
    total_files = len(json_files)
    logger.info(f"Found {total_files} JSON files to process.")

    # 7. Process each JSON file and upsert data in batches
    for i, file_path in enumerate(json_files):
        logger.info(f"Processing file {i + 1}/{total_files}: {file_path.name}")
        try:
            with open(file_path, "r") as f:
                video_analysis = VideoAnalysis(**json.load(f))

            documents = [chapter.content for chapter in video_analysis.chapters]
            if not documents:
                logger.warning(f"No chapters found in {file_path.name}, skipping.")
                continue

            # 8. Generate all embeddings for the file's chapters
            logger.info(f"Generating embeddings for {len(documents)} chapters...")
            dense_embeddings = list(dense_embed_model.passage_embed(documents))
            sparse_embeddings = list(sparse_embed_model.passage_embed(documents))
            late_embeddings = list(late_embed_model.passage_embed(documents))
            logger.info("Embeddings generated.")

            # 9. Create PointStructs for batch upsert
            points_to_upsert = []
            for idx, chapter in enumerate(video_analysis.chapters):
                payload = {
                    "video_id": video_analysis.video_id,
                    "chapter_id": chapter.chapter_id,
                    "heading": chapter.heading,
                    "content": chapter.content,
                    "timestamp": chapter.timestamp,
                }

                point = PointStruct(
                    id=uuid4().hex,  # Use a unique ID for each point
                    vector={
                        DENSE_MODEL: dense_embeddings[idx],
                        SPARSE_MODEL: sparse_embeddings[idx].as_object(),
                        LATE_INTERACTION_MODEL: late_embeddings[idx],
                    }, # type: ignore
                    payload=payload,
                )
                points_to_upsert.append(point)

            # 10. Upsert all points for the current file in a single batch
            if points_to_upsert:
                logger.info(f"Upserting {len(points_to_upsert)} points...")
                client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=points_to_upsert,
                    wait=True,
                )
                logger.info(f"Successfully upserted points from {file_path.name}")

        except json.JSONDecodeError:
            logger.error(f"Could not decode JSON from {file_path}")
        except Exception as e:
            logger.error(
                f"An error occurred while processing {file_path}: {e}", exc_info=True
            )


if __name__ == "__main__":
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)
    logger.add(
        log_path / "create_qdrant_index.log", rotation="10 MB", level="INFO"
    )
    create_index()
