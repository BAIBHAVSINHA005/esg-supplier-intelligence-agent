# app/rag/chunker.py

import re
import uuid
from typing import Dict, List, Optional


MAX_CHUNK_TOKENS = 60
CHUNK_OVERLAP_TOKENS = 15


def _subdivide_text(
    text: str,
    max_tokens: int = MAX_CHUNK_TOKENS,
    overlap_tokens: int = CHUNK_OVERLAP_TOKENS,
) -> list[tuple[str, int, int]]:
    """Split oversized text on whitespace-token boundaries with overlap.

    Original whitespace inside each subdivision is retained so extracted evidence
    can still be matched back to the indexed source text.
    """
    if max_tokens <= 0:
        raise ValueError("max_tokens must be greater than zero")
    if overlap_tokens < 0 or overlap_tokens >= max_tokens:
        raise ValueError("overlap_tokens must be between zero and max_tokens")

    matches = list(re.finditer(r"\S+", text))
    if not matches:
        return []
    if len(matches) <= max_tokens:
        return [(text, 0, len(matches))]

    subdivisions = []
    step = max_tokens - overlap_tokens
    for token_start in range(0, len(matches), step):
        token_end = min(token_start + max_tokens, len(matches))
        char_start = matches[token_start].start()
        char_end = matches[token_end - 1].end()
        subdivisions.append((text[char_start:char_end], token_start, token_end))
        if token_end == len(matches):
            break
    return subdivisions


def enhance_chunks(
    existing_chunks: List[Dict],
    *,
    source_filename: Optional[str] = None,
    assessment_id: Optional[str] = None,
    document_id: Optional[str] = None,
) -> List[Dict]:
    """
    MVP-2 PHASE 1: Chunk Enhancement

    WHY DOES THIS FILE EXIST?
    -------------------------

    In MVP-1, pdf_parser.py already creates paragraph chunks.

    Example:

        {
            "text": "Scope 3 emissions are estimated...",
            "page": 42,
            "section": None,
            "is_table": False
        }

    These chunks are stored in:

        state["document_chunks"]

    So we DO NOT need to create chunks from scratch.

    Instead, MVP-2 gradually prepares those chunks
    for retrieval and vector search.

    ------------------------------------------------

    WHY VERSION 1 IS SIMPLE
    -----------------------

    We are NOT doing:

    - embeddings
    - ChromaDB
    - vector search
    - retrieval

    yet.

    First we create a dedicated place where all future
    chunk-related logic will live.

    Think of this as:

        MVP-1 chunk
              ↓
        enhance_chunks()
              ↓
        MVP-2 retrieval-ready chunk

    ------------------------------------------------

    WHAT THIS FUNCTION DOES TODAY
    -----------------------------

    For each existing chunk:

    1. Keeps all current information
       (text, page, section, is_table)

    2. Subdivides oversized chunks into bounded, overlapping windows before
       embedding so content is not silently truncated by the embedding model.

    3. Adds a unique chunk_id and source/run metadata.

    4. Adds placeholder metadata that future
       retrieval code may use.

    ------------------------------------------------

    WHAT THIS FUNCTION WILL DO LATER
    --------------------------------

    Future versions may:

    - detect Principle 6 sections
    - detect tables
    - add ESG labels
    - add embeddings
    - add retrieval metadata

    without changing pdf_parser.py

    That separation keeps the architecture cleaner.
    """

    enhanced = []

    for chunk in existing_chunks:
        parent_chunk_id = chunk.get("chunk_id") or str(uuid.uuid4())
        subdivisions = _subdivide_text(chunk.get("text", ""))

        for subdivision_index, (text, token_start, token_end) in enumerate(
            subdivisions
        ):
            enhanced_chunk = {
                # Keep everything that already exists.
                **chunk,

                # Oversized PDF paragraphs are divided before embedding so later
                # content is not lost to the embedding model's input truncation.
                "text": text,
                "chunk_id": (
                    parent_chunk_id
                    if len(subdivisions) == 1
                    else f"{parent_chunk_id}:{subdivision_index}"
                ),
                "parent_chunk_id": parent_chunk_id,
                "subdivision_index": subdivision_index,
                "subdivision_count": len(subdivisions),
                "token_start": token_start,
                "token_end": token_end,

                # Placeholder for future Principle-level retrieval metadata.
                "principle": chunk.get("principle"),
                "embedding_ready": True,
                "source_filename": chunk.get("source_filename") or source_filename,
                "assessment_id": chunk.get("assessment_id") or assessment_id,
                "document_id": chunk.get("document_id") or document_id,
            }

            enhanced.append(enhanced_chunk)

    return enhanced
