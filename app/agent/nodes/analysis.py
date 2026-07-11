from app.agent.state import AssessmentState


def analysis_layer(state: AssessmentState) -> dict:
    """
    PHASE 3 PLACEHOLDER — Real implementation in Phase 3 (Days 9–13).

    Reads:
    - extracted_indicators
    - brsr_section_text

    Writes:
    - scope3_verdict
    - completeness_results
    - gaps

    CRITICAL:
    This node converts raw extracted indicators into business judgments.
    It is the first layer that answers:
    "How mature is this supplier's ESG disclosure?"
    """

    print(
        "[analysis_layer] PLACEHOLDER — would run Scope 3 classifier, "
        "completeness assessment, and gap detection"
    )

    return {
        "scope3_verdict": {
            "level": "not_found",
            "evidence": "PLACEHOLDER: evidence will appear here",
            "citation": "PLACEHOLDER: citation will appear here",

            # Future classifier outputs
            "maturity_signals": {
                "assurance": "not_found",
                "category_boundary": "not_found",
                "sbti": "not_found",
                "significant_partners": "not_found",
                "trend_data": "not_found"
            }
        },

        # Future:
        # [{"principle": 1, "status": "complete"}, ...]
        "completeness_results": [],

        # Future:
        # [{"gap_id": "G-01", "severity": "critical"}, ...]
        "gaps": [],
    }