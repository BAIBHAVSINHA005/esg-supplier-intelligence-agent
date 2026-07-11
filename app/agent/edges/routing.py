from app.agent.state import AssessmentState


def route_after_quality_check(state: AssessmentState) -> str:
    """
    Conditional routing function called by LangGraph after quality_check completes.

    Reads: state["document_failure"]
    Returns: the name of the next node to execute

    ONLY ONE FIELD DRIVES THIS DECISION: document_failure.
    Do not add logic here that belongs in quality_check.
    Do not read confidence_level, is_machine_readable, or brsr_section_found here.
    Those fields influence what quality_check writes to document_failure.
    This function only reads the result.

    Return values must exactly match the keys in add_conditional_edges mapping dict.
    If this function returns a string not in that dict, LangGraph raises a
    runtime ValueError — not a compile-time error.
    """
    if state.get("document_failure", False):
        print("[routing] document_failure=True → routing to handle_failure")
        return "handle_failure"

    print("[routing] document_failure=False → routing to extract_indicators")
    return "extract_indicators"
