# app/rag/embeddings.py

"""
Embedding utilities for MVP-2.

Purpose:
Convert chunk text into numerical vectors that
can later be stored in ChromaDB.

Current model:
all-MiniLM-L6-v2

Why this model?

- Small
- Fast
- Free
- Commonly used for RAG prototypes
"""

from sentence_transformers import SentenceTransformer


# Load once on first use. Importing retrieval utilities should not allocate the
# model when callers provide or mock embeddings themselves.
_model = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def get_embedding(text: str) -> list[float]:
    """
    Convert a text string into an embedding vector.

    Example:

        "Scope 3 emissions disclosed"

            ↓

        [0.123, -0.441, 0.881, ...]

    Returns:
        list[float]
    """

    vector = _get_model().encode(text)

    return vector.tolist()
