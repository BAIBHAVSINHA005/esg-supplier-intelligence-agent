from app.agent.state import AssessmentState
from app.rag.retriever import index_chunks


def index_document(state: AssessmentState) -> dict:
    """
    Node: Index the uploaded document chunks into ChromaDB.

    Reads:
        document_chunks

    Writes:
        None (side-effect only)

    Raises:
        document_failure if indexing fails.
    """

    print("[index_document]")

    chunks = state.get("document_chunks", [])

    if not chunks:
        print("[index_document] No document chunks found.")

        return {
            "document_failure": True,
            "document_failure_reason": "No document chunks available for indexing."
        }

    try:
        print(f"[index_document] Indexing {len(chunks)} chunks...")

        index_chunks(chunks)

        print("[index_document] Indexing complete.")

        return {}

    except Exception as e:
        print(f"[index_document] ERROR: {e}")

        return {
            "document_failure": True,
            "document_failure_reason": f"Failed to index document: {str(e)}"
        }