# app/rag/retriever.py

from app.rag.client import get_client
from app.rag.embeddings import get_embedding


COLLECTION_NAME = "esg_document_chunks"


# --------------------------------------------------
# 1. Create / Load Collection
# --------------------------------------------------

def get_collection():
    """
    Create the collection if it does not exist.
    Otherwise load the existing one.
    """

    client = get_client()

    return client.get_or_create_collection(
        name=COLLECTION_NAME
    )


# --------------------------------------------------
# 2. Index Chunks
# --------------------------------------------------

def index_chunks(chunks, document_id: str):
    """
    Store document chunks inside ChromaDB.
    """

    collection = get_collection()

    for chunk in chunks:

        metadata = {
            "page": chunk["page"],
            "document_id": document_id,
        }
        for metadata_key in (
            "source_filename",
            "assessment_id",
            "parent_chunk_id",
            "subdivision_index",
            "subdivision_count",
            "token_start",
            "token_end",
        ):
            metadata_value = chunk.get(metadata_key)
            if metadata_value is not None:
                metadata[metadata_key] = metadata_value

        collection.add(
            ids=[chunk["chunk_id"]],
            documents=[chunk["text"]],
            metadatas=[metadata],
            embeddings=[
                get_embedding(chunk["text"])
            ]
        )


# --------------------------------------------------
# 3. Retrieve Chunks
# --------------------------------------------------

def retrieve_chunks(query: str, document_id: str, k: int = 5):
    """
    Retrieve the most relevant chunks
    for a user query.
    """

    collection = get_collection()

    results = collection.query(
        query_embeddings=[
            get_embedding(query)
        ],
        n_results=k,
        where={"document_id": document_id},
    )

    return results
