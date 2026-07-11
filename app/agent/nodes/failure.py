# app/agent/nodes/failure.py

from datetime import datetime
from app.agent.state import AssessmentState


FAILURE_DISCLAIMER = (
    "Assessment could not be completed due to a document processing failure. "
    "Please verify the uploaded file is a machine-readable BRSR PDF and try again."
)


def handle_failure(state: AssessmentState) -> dict:
    """
    Active on ALL phases — this node is complete as written.

    Real responsibility (same in placeholder and production):
    - Run when document_failure == True (set by quality_check)
    - Produce a minimal error brief instead of a full ESG assessment
    - The error brief contains the failure reason and a directive
    - Does NOT call Claude, does NOT touch ChromaDB

    This is the terminal node on the FAILURE path.
    All downstream analysis nodes (extract, analysis, confidence, questions, brief)
    DO NOT run when this node executes.

    State fields like extracted_indicators, scope3_verdict, gaps, and
    followup_questions will retain their initialised values (empty dicts and lists)
    because no node on this path writes to them.
    This is correct behaviour — do not try to populate them here.
    """
    failure_reason = state.get("document_failure_reason") or "Unknown document processing error."
    print(f"[handle_failure] Document could not be processed: {failure_reason}")

    brief = {
        "disclaimer": FAILURE_DISCLAIMER,
        "header": {
            "supplier_name": state["supplier_name"],
            "source_filename": state["source_filename"],
            "assessment_id": state["assessment_id"],
            "generated_at": datetime.utcnow().isoformat(),
            "confidence_level": "low",
            "confidence_directive": (
                "Document processing failed. Do not use this output for "
                "any procurement or compliance decision."
            ),
            "hitl_flag": True,
        },
        "error": failure_reason,
        "completeness_assessment": [],
        "scope3_verdict": None,
        "gaps": [],
        "followup_questions": [],
    }

    return {
        "brief": brief,
        "error": failure_reason,
    }
