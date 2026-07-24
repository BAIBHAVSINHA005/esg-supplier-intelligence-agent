# app/agent/nodes/extract.py

from app.agent.state import AssessmentState
from app.schemas.loader import load_schema, get_indicators
from app.extraction.llm_extractor import LLMExtractor
from app.extraction.schemas import IndicatorExtractionResult, to_pipeline_dict


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

    retrieved_context = state.get("retrieved_context", {})

    if not retrieved_context:
        print("[extract_indicators] WARNING: No retrieved context found")
        return {"extracted_indicators": {}}

    # Load schema
    schema = load_schema("brsr_v2023")

    # Phase 3: Principle 6 only
    principle_6_indicators = get_indicators(
        schema,
        "principle_6"
    )

    print(
        f"[extract_indicators] Running LLM extraction for "
        f"{len(principle_6_indicators)} indicators"
    )

    llm_extractor = LLMExtractor()
    principle_6_results = {}

    for indicator_id, indicator_def in principle_6_indicators.items():
        retrieval_result = retrieved_context.get(indicator_id, {})
        documents = retrieval_result.get("documents", [[]])
        chunks = documents[0] if documents else []
        context = "\n\n".join(chunks)

        print(
            f"[extract_indicators] {indicator_id}: {len(chunks)} chunk(s)"
        )

        extraction_result = llm_extractor.extract_indicator(
            indicator_id=indicator_id,
            indicator_name=indicator_def["name"],
            indicator_description=indicator_def["description"],
            context=context,
            citation=indicator_def.get("brsr_indicator_ref", ""),
        )

        if isinstance(extraction_result, IndicatorExtractionResult):
            principle_6_results[indicator_id] = to_pipeline_dict(extraction_result)
        else:
            principle_6_results[indicator_id] = extraction_result

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
