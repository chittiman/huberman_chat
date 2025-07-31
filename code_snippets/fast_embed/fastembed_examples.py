import marimo

__generated_with = "0.14.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from fastembed import LateInteractionTextEmbedding,TextEmbedding

    return LateInteractionTextEmbedding, TextEmbedding, mo


@app.cell
def _(mo):
    mo.md(
        r"""
    ##Embedding models have 3 methods which will return embeddings.
    ## All of them can take str or List(str) as input
    ### .embed() method gives embeddings suitable for clustering, etc
    ### .passage_embed() method is for documents used to answer.
    ### .query_embed() method is for embeddings suitable for queries
    """
    )
    return


@app.cell
def _():
    sentences = ["Ramu is going to school", "Rama killed Ravana"]
    queries = ["Where is Ramu going?", "Whop killed Ravan?"]
    return queries, sentences


@app.cell
def _(TextEmbedding):
    text_embed = TextEmbedding("jinaai/jina-embeddings-v2-base-en")
    #Sentence Embedding Model
    return (text_embed,)


@app.cell
def _(sentences, text_embed):
    sent_embs = list(text_embed.passage_embed(sentences))
    #passage_embed method is to encode documents which are going to be queried
    #It will return a generator.

    print(len(sent_embs))
    # >> 2
    print(type(sent_embs[0]))
    # >> <class 'numpy.ndarray'>
    print(sent_embs[0].shape)
    # >> (768,)

    return


@app.cell
def _(queries, text_embed):
    query_embs = list(text_embed.query_embed(queries))
    #query_embed method is to encode queries
    #It will return a generator.

    print(len(query_embs))
    # >> 2
    print(type(query_embs[0]))
    # >> <class 'numpy.ndarray'>
    print(query_embs[0].shape)
    # >> (768,)
    return


@app.cell
def _(LateInteractionTextEmbedding):
    LateInteractionTextEmbedding.list_supported_models()[-1]
    # list_supported_models method gives list of supported models for that class
    return


@app.cell
def _(LateInteractionTextEmbedding):
    late_embed = LateInteractionTextEmbedding("jinaai/jina-colbert-v2")
    # This is late interaction colbert style model. COmputationally heavy. Suitable for reranking
    return (late_embed,)


@app.cell
def _(late_embed, sentences):
    late_sent_embs = list(late_embed.passage_embed(sentences))
    #passage_embed method is to encode documents which are going to be queried
    #It will return a generator.

    print(len(late_sent_embs))
    # >> 2
    print(type(late_sent_embs[0]))
    # >> <class 'numpy.ndarray'>
    print(late_sent_embs[0].shape)
    # >> (9, 128)
    # 9 is number of tokens in the sentence , 128 is the embedding size

    return


@app.cell
def _(late_embed, queries):
    late_query_embs = list(late_embed.query_embed(queries))
    #query_embed method is to encode queries
    #It will return a generator.

    print(len(late_query_embs))
    # >> 2
    print(type(late_query_embs[0]))
    # >> <class 'numpy.ndarray'>
    print(late_query_embs[0].shape)
    # >> (32, 128)
    # 32 is number of tokens in the sentence , 128 is the embedding size
    return


if __name__ == "__main__":
    app.run()
