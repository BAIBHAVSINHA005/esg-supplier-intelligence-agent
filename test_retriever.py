# app/agent/nodes/retrieve.py

from app.agent.state import AssessmentState
from app.rag.retriever import retrieve_chunks


def retrieve_context(state: AssessmentState) -> dict:
    """
    Node 3A: Retrieval Layer

    Reads:
        document_chunks

    Writes:
        retrieved_context

    MVP-2:
        Retrieve top-k ESG-relevant chunks
        from ChromaDB and store them in state.
    """

    print("[retrieve_context]")

    results = retrieve_chunks(
        query="ESG indicators",
        k=5
    )

    num_chunks = len(
        results.get("documents", [[]])[0]
    )

    print(
        f"[retrieve_context] Retrieved {num_chunks} chunks"
    )

    return {
        "retrieved_context": results
    }