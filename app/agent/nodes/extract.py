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
    # Build a unified retrieval context from all indicator-specific
    # searches. This is a temporary compatibility layer so the
    # existing keyword extractor can continue to operate on a single
    # text corpus until the LLM extractor replaces it.
    # --------------------------------------------------------------------------------------------------

    retrieved_context = state.get("retrieved_context", {})

    if not retrieved_context:
        print("[extract_indicators] WARNING: No retrieved context found")
        return {"extracted_indicators": {}}

    all_chunks = []

    for indicator_id, result in retrieved_context.items():

        docs = result.get("documents", [[]])[0]

        print(
            f"[extract_indicators] {indicator_id}: {len(docs)} chunk(s)"
        )

        all_chunks.extend(docs)

    if not all_chunks:
        print("[extract_indicators] WARNING: No retrieved chunks found")
        return {"extracted_indicators": {}}

    # Remove duplicate chunks while preserving order
    unique_chunks = list(dict.fromkeys(all_chunks))

    brsr_text = "\n\n".join(unique_chunks)

    print(
        f"[extract_indicators] Combined "
        f"{len(unique_chunks)} unique retrieved chunks "
        f"({len(brsr_text):,} chars)"
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

    # ESG classification starts here
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