import marimo

__generated_with = "0.14.13"
app = marimo.App(width="medium")


@app.cell
def _():
    from qdrant_client import QdrantClient
    from fastembed import LateInteractionTextEmbedding,TextEmbedding,SparseTextEmbedding
    from qdrant_client.models import Distance, VectorParams, models, PointStruct
    import marimo as mo
    return (
        LateInteractionTextEmbedding,
        PointStruct,
        QdrantClient,
        SparseTextEmbedding,
        TextEmbedding,
        mo,
        models,
    )


@app.cell
def _(LateInteractionTextEmbedding, SparseTextEmbedding, TextEmbedding):
    dense_embed = TextEmbedding("jinaai/jina-embeddings-v2-base-en")
    late_embed = LateInteractionTextEmbedding("jinaai/jina-colbert-v2")
    bm25_embed = SparseTextEmbedding("Qdrant/bm25")
    return bm25_embed, dense_embed, late_embed


@app.cell(hide_code=True)
def _():
    docs = ["There is no evidence that smoking cannabis is inherently better than smoking cigarettes, though the typical dose for cannabis appears to be significantly lower. Heavy cigarette smoking, such as 20-30 pack-years, dramatically increases the risk of various cancers, including lung cancer, and cardiovascular and cerebrovascular diseases. The speaker notes that while not a THC expert, they imagine marijuana smokers do not consume as much as heavy cigarette smokers.",
    "On a joint-to-cigarette basis, the immediate harm is likely equivalent. However, a person smoking one joint a day ingests a significantly smaller cumulative dose compared to someone smoking a pack of cigarettes daily, suggesting a lower overall risk, though it's not without downsides. The speaker cautions that the overall risk might not fully track linearly due to dose differences.",
    "Vaping is not a good idea, and data on its long-term effects remains surprisingly sparse. Its only potential advantage is as a harm reduction tool for those trying to quit smoking, making it the lesser of two evils. The ideal scenario is to avoid all such habits; safer nicotine delivery methods like lozenges and gum are preferable to vaping. Vaping is positioned as less harmful than smoking but still carries significant risks compared to non-inhalation methods.",
    "Discussions about cannabis often become contentious, with unhelpful comparisons to alcohol's harm. While cannabis undeniably has medical applications, particularly pure CBD forms for treating certain epilepsies (e.g., Charlotte's Web), high-THC cannabis clearly predisposes young males to later-onset psychosis. This data is becoming clear enough that people should be aware of these risks when making decisions.",
    "It is very clear that the chemical constituents in vape products are harmful, containing carcinogens and other substances, many of which cross the blood-brain barrier. The speaker expresses concern about small inorganic molecules being maintained in neurons for many years, noting that the long-term health experiment of vaping is currently ongoing, primarily among young people.",
    "If possible, people should avoid smoking and vaping. For those who choose to use nicotine or cannabis, alternative delivery devices such as tinctures, patches, gums, and edibles are available. These methods can help offset the significant health risks associated with inhaling substances directly into the lungs.",
    "The surface area of the lungs' alveolar air sacs is remarkably large, capable of covering a tennis court when spread out. This immense surface area makes the body incredibly adept at absorbing anything inhaled. Therefore, it is crucial to be mindful of what is inhaled, as the body's efficient gas exchange system will readily absorb other substances.",
    "The principle of lung absorption also applies to air pollution, particularly PM 2.5 particulates (less than 2.5 microns), which directly enter the body. This is a strong argument for avoiding air pollution. The speaker asserts that deaths from particulate matter due to burning coal far outnumber those from CO2 emissions. Wildfires offer a clear example of how air pollution immediately impacts breathing and can embed harmful particulates in brain tissue and other organs for extended periods."]
    return (docs,)


@app.cell
def _(bm25_embed, dense_embed, docs, late_embed):
    bm25_embeddings = list(bm25_embed.embed(doc for doc in docs))
    # Dense and late embeddings wwill be list of numpy arrays
    dense_embeddings = list(dense_embed.embed(doc for doc in docs))
    late_embeddings = list(late_embed.embed(doc for doc in docs))
    return bm25_embeddings, dense_embeddings, late_embeddings


@app.cell
def _(dense_embeddings, late_embeddings):
    print(dense_embeddings[0].shape)
    # >> (768,) -> This is a 1D Array
    print(late_embeddings[0].shape)
    # >> (119, 128) -> This is a 2D Array
    return


@app.cell
def _(QdrantClient, dense_embeddings, late_embeddings, models):
    client = QdrantClient(url="http://localhost:6333")

    client.create_collection(
        "hybrid-search",
        vectors_config={
            "jina-embeddings-v2-base-en": models.VectorParams(
                size=len(dense_embeddings[0]),
                distance=models.Distance.COSINE,
            ), # This is for dense embeddings
            "jina-colbert-v2": models.VectorParams(
                size=len(late_embeddings[0][0]),
                distance=models.Distance.COSINE,
                multivector_config=models.MultiVectorConfig(
                    comparator=models.MultiVectorComparator.MAX_SIM,
                ),
                hnsw_config=models.HnswConfigDiff(m=0)  #  Disable HNSW for reranking. done on small docs set
            ), # This is for late embeddings
        },
        sparse_vectors_config={
            "bm25": models.SparseVectorParams(modifier=models.Modifier.IDF
            )
        }
    )
    return (client,)


@app.cell
def _(
    PointStruct,
    bm25_embeddings,
    client,
    dense_embeddings,
    docs,
    late_embeddings,
):
    points = []
    for idx, (dense_embedding, bm25_embedding, late_interaction_embedding, doc) in enumerate(zip(dense_embeddings, bm25_embeddings, late_embeddings, docs)):
  
        point = PointStruct(
            id=idx,
            vector={
                "jina-embeddings-v2-base-en": dense_embedding,
                "bm25": bm25_embedding.as_object(),
                "jina-colbert-v2": late_interaction_embedding,
            },
            payload={"document": doc}
        )
        points.append(point)

    operation_info = client.upsert(
        collection_name="hybrid-search",
        points=points
    )
    return


@app.cell
def _():
    queries = [
        "Is Vaping safe than smoking??",
        "Does taking ganja bad for health??"
    ]
    return (queries,)


@app.cell
def _(bm25_embed, dense_embed, late_embed, queries):
    query = queries[1]
    dense_vectors = next(dense_embed.query_embed(query))
    sparse_vectors = next(bm25_embed.query_embed(query))
    late_vectors = next(late_embed.query_embed(query))
    return dense_vectors, late_vectors, sparse_vectors


@app.cell
def _(client, models, sparse_vectors):
    # Plain BM25 Search
    results_bm25 = client.query_points(
             "hybrid-search",
            query=models.SparseVector(**sparse_vectors.as_object()),
            using="bm25",
            with_payload=True,
            limit=10,
    )
    return


@app.cell
def _(client, dense_vectors):
    # Only Vector Search
    results_embed_search = client.query_points(
             "hybrid-search",
            query=dense_vectors,
            using="jina-embeddings-v2-base-en",
            with_payload=True,
            limit=10,
    )
    return


@app.cell
def _(dense_vectors, models, sparse_vectors):
    # Prefetching vectors for Hybrid Search
    prefetch = [
            models.Prefetch(
                query=dense_vectors,
                using="jina-embeddings-v2-base-en",
                limit=20,
            ),
            models.Prefetch(
                query=models.SparseVector(**sparse_vectors.as_object()),
                using="bm25",
                limit=20,
            ),
        ]
    return (prefetch,)


@app.cell
def _(client, late_vectors, prefetch):
    # Hybrid Search followed by reranking with late interaction models
    results_hybrid_rerank_with_colbert = client.query_points(
             "hybrid-search",
            prefetch=prefetch,
            query=late_vectors,
            using="jina-colbert-v2",
            with_payload=True,
            limit=10,
    )
    return


@app.cell
def _(client, models, prefetch):
    # Hybrid Search followed by reranking with Reciprocal Rank Fusion
    results_hybrid_rerank_with_rrf = client.query_points(
             "hybrid-search",
            prefetch=prefetch,
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            with_payload=True,
            limit=3,
    )

    return (results_hybrid_rerank_with_rrf,)


@app.cell
def _(results_hybrid_rerank_with_rrf):
    results_hybrid_rerank_with_rrf.model_dump()
    #Output is a Query Response pydantic model, it has model_dump method which will convert output to json
    # Output in below markdown cell
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Sample output of Query response object
    ```json
    {
      "points": [
        {
          "id": 4,
          "version": 1,
          "score": 0.6666667,
          "payload": {
            "document": "It is very clear that the chemical constituents in vape products are harmful, containing carcinogens and other substances, many of which cross the blood-brain barrier. The speaker expresses concern about small inorganic molecules being maintained in neurons for many years, noting that the long-term health experiment of vaping is currently ongoing, primarily among young people."
          },
          "vector": None,
          "shard_key": None,
          "order_value": None
        },
        {
          "id": 5,
          "version": 1,
          "score": 0.64285713,
          "payload": {
            "document": "If possible, people should avoid smoking and vaping. For those who choose to use nicotine or cannabis, alternative delivery devices such as tinctures, patches, gums, and edibles are available. These methods can help offset the significant health risks associated with inhaling substances directly into the lungs."
          },
          "vector": None,
          "shard_key": None,
          "order_value": None
        },
        {
          "id": 0,
          "version": 1,
          "score": 0.5,
          "payload": {
            "document": "There is no evidence that smoking cannabis is inherently better than smoking cigarettes, though the typical dose for cannabis appears to be significantly lower. Heavy cigarette smoking, such as 20-30 pack-years, dramatically increases the risk of various cancers, including lung cancer, and cardiovascular and cerebrovascular diseases. The speaker notes that while not a THC expert, they imagine marijuana smokers do not consume as much as heavy cigarette smokers."
          },
          "vector": None,
          "shard_key": None,
          "order_value": None
        }
      ]
    }
    ```
    """
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
