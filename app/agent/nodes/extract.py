# app/agent/nodes/extract.py

from app.agent.state import AssessmentState
from app.schemas.loader import load_schema, get_indicators
from app.extraction.llm_extractor import LLMExtractor
from app.extraction.schemas import (
    IndicatorExtractionResult,
    make_error_result,
    to_pipeline_dict,
)


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
        return {"extracted_indicators": {}, "extraction_errors": []}

    retrieved_context = state.get("retrieved_context", {})

    if not retrieved_context:
        print("[extract_indicators] WARNING: No retrieved context found")
        return {"extracted_indicators": {}, "extraction_errors": []}

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

    principle_6_results = {}
    extraction_errors = []

    try:
        llm_extractor = LLMExtractor()
    except Exception as exc:
        error_code = LLMExtractor._error_code_for(exc)
        print(f"[extract_indicators] LLM client initialization failed: {exc}")
        for indicator_id, indicator_def in principle_6_indicators.items():
            error_result = make_error_result(
                indicator_id=indicator_id,
                citation=indicator_def.get("brsr_indicator_ref", ""),
                error_code=error_code,
                error_message=str(exc),
            )
            principle_6_results[indicator_id] = error_result
            extraction_errors.append(
                {
                    "indicator_id": indicator_id,
                    "indicator_name": indicator_def["name"],
                    "error_code": error_code,
                    "error_message": str(exc),
                    "citation": error_result["citation"],
                }
            )

        return {
            "extracted_indicators": {"principle_6": principle_6_results},
            "extraction_errors": extraction_errors,
        }

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

        normalized_result = principle_6_results[indicator_id]
        if normalized_result.get("state") == "extraction_error":
            extraction_errors.append(
                {
                    "indicator_id": indicator_id,
                    "indicator_name": indicator_def["name"],
                    "error_code": normalized_result.get(
                        "error_code", "extraction_error"
                    ),
                    "error_message": normalized_result.get("error_message", ""),
                    "citation": normalized_result.get("citation", ""),
                }
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
        },
        "extraction_errors": extraction_errors,
    }
