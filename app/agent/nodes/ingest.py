
from app.agent.state import AssessmentState


def ingest_document(state: AssessmentState) -> dict:
    """
    PHASE 2 PLACEHOLDER — Real implementation in Phase 2 (Day 4).

    Real responsibility:
    - Open document_bytes using PyMuPDF (fitz.open(stream=...))
    - Extract text from every page using page.get_text("text")
    - Split text into chunks with page and section metadata
    - Return document_text, document_chunks, num_pages

    This node does NOT call LLM.
    This node does NOT touch ChromaDB.
    This node only transforms bytes → text.
    """ 
    print(f"[ingest_document] PLACEHOLDER — would parse PDF: {state['source_filename']}")

    return {
    "document_text": (
        "PLACEHOLDER: full PDF text will appear here "
        "once PyMuPDF ingestion is implemented."
    ),
    "document_chunks": [],
    "num_pages": 0,
    }