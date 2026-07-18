# app/agent/nodes/extract.py

from app.agent.state import AssessmentState
from app.schemas.loader import load_schema, get_indicators
from app.extraction.keyword_extractor import extract_principle_indicators


def extract_indicators(state: AssessmentState) -> dict:
    """
    Node 3: Extract ESG indicator data from retrieved ESG context.

    Reads:
        retrieved_context
        document_failure

    Writes:
        extracted_indicators
    """

    print("[extract_indicators]")

    # If upstream nodes failed, skip extraction
    if state.get("document_failure", False):
        print("[extract_indicators] Upstream document failure — skipping extraction")
        return {"extracted_indicators": {}}

    # --------------------------------------------------
    # Use retrieved chunks from ChromaDB
    # --------------------------------------------------

    retrieved_docs = (
        state
        .get("retrieved_context", {})
        .get("documents", [[]])[0]
    )

    if not retrieved_docs:
        print("[extract_indicators] WARNING: No retrieved chunks found")
        return {"extracted_indicators": {}}

    brsr_text = "\n\n".join(retrieved_docs)

    print(
        f"[extract_indicators] Extracting from "
        f"{len(brsr_text):,} chars of retrieved context "
        f"({len(retrieved_docs)} chunks)"
    )

    # Load schema
    schema = load_schema("brsr_v2023")

    # Phase 3: Principle 6 only
    principle_6_indicators = get_indicators(
        schema,
        "principle_6"
    )

    print(
        f"[extract_indicators] Running keyword extraction for "
        f"{len(principle_6_indicators)} indicators"
    )

    #ESG classification starts here
    principle_6_results = extract_principle_indicators(
        principle_indicators=principle_6_indicators,
        brsr_section_text=brsr_text,
    )

    # Count results by state for logging
    state_counts = {}

    for result in principle_6_results.values():
        s = result.get("state", "unknown")
        state_counts[s] = state_counts.get(s, 0) + 1

    print(f"[extract_indicators] Results: {state_counts}")

    return {
        "extracted_indicators": {
            "principle_6": principle_6_results
        }
    }