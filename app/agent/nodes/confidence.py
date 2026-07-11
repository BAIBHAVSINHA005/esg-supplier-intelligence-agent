from app.agent.state import AssessmentState


def assess_confidence(state: AssessmentState) -> dict:
    """
    PHASE 3 PLACEHOLDER — Real implementation in Phase 3 (Day 20).

    Real responsibility:
    - Read extraction_confidence_score from quality_check
    - Count how many indicators were successfully extracted vs not_found
    - Assign confidence_level:
        "high"   if score >= 0.8 AND extraction ratio >= 0.8 AND no uncertain fields
        "medium" if score >= 0.5 AND extraction ratio >= 0.5
        "low"    otherwise
    - Set confidence_directive to the correct fixed behavioural text
    - Set hitl_flag = True when confidence_level == "low"
    - Populate uncertain_fields with names of fields where extraction was unreliable

    This node does NOT call Claude.
    This node does NOT touch ChromaDB.
    This node is a PURE FUNCTION — deterministic from inputs, no side effects.
    Write unit tests for it before running it through the graph.

    IMPORTANT: hitl_flag does NOT change routing.
    It is a field that propagates into the brief — it does not stop the pipeline.
    The pipeline always runs to compile_brief regardless of confidence level.
    """
    print(
    "[assess_confidence] PLACEHOLDER — would calculate "
    "assessment confidence"
)

    return {
        "confidence_level": "high",
        "confidence_directive": "PLACEHOLDER: directive will appear here.",
        "hitl_flag": False,
        "uncertain_fields": [],
    }

