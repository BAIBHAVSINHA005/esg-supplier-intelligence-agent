from datetime import datetime
from app.agent.state import AssessmentState


DISCLAIMER = (
    "This assessment is based solely on the uploaded BRSR filing. "
    "Disclosures in separate sustainability reports, CDP submissions, "
    "GRI reports, or supplementary documents were not reviewed and "
    "are not reflected in this brief."
)


def compile_brief(state: AssessmentState) -> dict:
    """
    Generate final ESG Intelligence Brief.

    This node assembles outputs from:
    - analysis_layer
    - assess_confidence
    - generate_questions

    into a single structured brief object.

    Real responsibility:
    - Assemble ALL state outputs into the final structured ESG Intelligence Brief
    - This node does NOT call Claude — it is pure assembly
    - Structure:
        disclaimer (always first)
        header: supplier_name, source_filename, assessment_id, timestamp,
                confidence_level, confidence_directive, hitl_flag
        completeness_assessment: completeness_results (from analysis_layer)
        scope3_verdict: (from analysis_layer)
        gaps: (from analysis_layer)
        followup_questions: (from generate_questions)
        uncertain_fields: (from assess_confidence — used to render [⚠] markers)

    This node reads: ALL analysis and confidence fields
    This node writes: brief
    This node is the LAST node on the success path.
    """
    print(f"[compile_brief] Assembling ESG Intelligence Brief for: "
          f"{state['supplier_name']}")

    brief = {
        "disclaimer": DISCLAIMER,
        "header": {
            "supplier_name": state["supplier_name"],
            "source_filename": state["source_filename"],
            "assessment_id": state["assessment_id"],
            "generated_at": datetime.utcnow().isoformat(),
            "confidence_level": state["confidence_level"],
            "confidence_directive": state["confidence_directive"],
            "hitl_flag": state["hitl_flag"],
        },
        "completeness_assessment": state["completeness_results"],
        "scope3_verdict": state["scope3_verdict"],
        "gaps": state["gaps"],
        "followup_questions": state["followup_questions"],
        "uncertain_fields": state["uncertain_fields"],
        "status": "brief_generated",
    }

    return {"brief": brief}

