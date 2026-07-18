
#app/agent/nodes/ingest.py_MVP1_ORIGINALCODE

# app/agent/nodes/ingest.py

#import fitz
from app.agent.state import AssessmentState
from app.extraction.pdf_parser import extract_text_from_bytes
from app.rag.chunker import enhance_chunks


def ingest_document(state: AssessmentState) -> dict:
    """
    Node 1: Extract text and page-level chunks from the uploaded PDF.

    Reads:  document_bytes, source_filename
    Writes: document_text, document_chunks, num_pages
            document_failure, document_failure_reason (on parse error)

    No LLM call. No ChromaDB. Pure document processing.
    """
    print("[ingest_document]")

    pdf_bytes = state.get("document_bytes", b"")

    if not pdf_bytes:
        return {
            "document_text": "",
            "document_chunks": [],
            "num_pages": 0,
            "document_failure": True,
            "document_failure_reason": "No document bytes received. Please upload a PDF file."
        }

    try:
        full_text, chunks, num_pages = extract_text_from_bytes(pdf_bytes)
        chunks = enhance_chunks(chunks)
        #debugging
        print(f"[ingest_document] Enhanced {len(chunks)} chunks")
        print(f"[ingest_document] Extracted {len(full_text):,} chars from {num_pages} pages")
        return {
            "document_text": full_text,
            "document_chunks": chunks,
            "num_pages": num_pages,
            "document_failure": False,
            "document_failure_reason": None,
        }
    except Exception as e:
        print(f"[ingest_document] ERROR: {e}")
        return {
            "document_text": "",
            "document_chunks": [],
            "num_pages": 0,
            "document_failure": True,
            "document_failure_reason": f"PDF could not be opened or parsed: {str(e)}"
        }