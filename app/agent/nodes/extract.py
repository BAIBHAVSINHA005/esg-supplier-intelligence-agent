from app.agent.state import AssessmentState


def extract_indicators(state: AssessmentState) -> dict:
    """
    PHASE 3 PLACEHOLDER

    Reads:
    - brsr_section_text
    - assessment_id

    Writes:
    - extracted_indicators
    """

    print(
        "[extract_indicators] PLACEHOLDER — would extract "
        f"BRSR indicators for: {state['supplier_name']}"
    )

    return {
        "extracted_indicators": {
            "principle_6": {
                "scope_3_emissions": {
                    "state": "not_found",
                    "value": "",
                    "citation": (
                        "PLACEHOLDER: real citation will appear here"
                    )
                }
            }
        }
    }