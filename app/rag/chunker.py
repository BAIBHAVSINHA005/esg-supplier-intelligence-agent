# app/rag/chunker.py

from typing import List, Dict
import uuid


def enhance_chunks(existing_chunks: List[Dict]) -> List[Dict]:
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

    2. Adds a unique chunk_id

    3. Adds placeholder metadata that future
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

    for idx, chunk in enumerate(existing_chunks):

        enhanced_chunk = {

            # Keep everything that already exists
            **chunk,

            # Every chunk gets a unique ID.
            #
            # Future use:
            # - retrieval
            # - citations
            # - evidence tracking
            #
            # Example:
            #
            # chunk_42
            #
            # Later:
            #
            # "Evidence found in chunk_42"
            #
            "chunk_id": str(uuid.uuid4()),
        

            # Placeholder.
            #
            # Future:
            #
            # Principle 6
            # Principle 5
            # Principle 2
            #
            # Currently unknown.
            #
            "principle": None,

            # Marker showing this chunk can be
            # passed into future embedding logic.
            #
            # Not actually used yet.
            #
            "embedding_ready": True,
        }

        enhanced.append(enhanced_chunk)

    return enhanced