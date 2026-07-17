# app/rag/client.py

"""
Single ChromaDB client for the project.

All retrieval code should use this client.

Avoid creating multiple clients throughout the codebase.
"""

import chromadb


_client = chromadb.PersistentClient(
    path="vector_db"
)


def get_client():
    """
    Return the singleton Chroma client.
    """

    return _client