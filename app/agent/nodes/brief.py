from datetime import datetime
from app.agent.state import AssessmentState
from app.agent.evidence import build_evidence_register, format_reference


DISCLAIMER = (
    "This assessment is based solely on the uploaded BRSR filing. "
    "Disclosures in separate sustainability reports, CDP submissions, "
    "GRI reports, or supplementary documents were not reviewed and "
    "are not reflected in this brief."
)


def _scope3_assessment_narrative(scope3_verdict: dict | None) -> str:
    """Explain the business implication of the existing Scope 3 verdict."""
    verdict = scope3_verdict or {}
    level = verdict.get("level", "extraction_error")

    narratives = {
        "disclosed": (
            "The reported information can serve as a preliminary input to supplier "
            "emissions analysis. Procurement and sustainability teams should confirm "
            "the reporting boundary, category coverage, and supporting evidence before "
            "using it for comparison or value-chain accounting."
        ),
        "scope3_ready": (
            "The information is usable as a preliminary supplier-emissions input. "
            "Before relying on it for comparison or value-chain accounting, teams "
            "should confirm category coverage, organizational boundaries, and any "
            "assurance limitations."
        ),
        "partial": (
            "The missing disclosure element limits comparability and prevents reliable "
            "use in the buyer's value-chain inventory. Until the disclosure is "
            "complete, teams should treat it as non-comparable supplier data."
        ),
        "claim_only": (
            "Qualitative recognition alone cannot be aggregated into the buyer's "
            "value-chain inventory or used for consistent supplier comparison. It "
            "therefore provides awareness of the issue, but not decision-useful data."
        ),
        "materiality_claim": (
            "The claim does not provide enough support to evaluate whether relevant "
            "value-chain emissions were excluded. Without the underlying materiality "
            "assessment and boundary, the buyer cannot validate the position."
        ),
        "not_found": (
            "The absence of usable data in this filing creates a supplier-information "
            "gap for value-chain accounting and comparison; it does not indicate zero "
            "emissions or remove the supplier's value-chain exposure."
        ),
        "extraction_error": (
            "No conclusion about disclosure can be drawn from this result. A reviewer "
            "should inspect the cited source section before procurement or "
            "sustainability teams use the assessment."
        ),
        "unassessed": (
            "No conclusion about disclosure can be drawn from this result. A reviewer "
            "should inspect the cited source section before procurement or "
            "sustainability teams use the assessment."
        ),
    }

    return narratives.get(
        level,
        "The Scope 3 result is not available in a recognized verdict state. "
        "Procurement and sustainability teams should review the source evidence "
        "before using it.",
    )


def _executive_summary(state: AssessmentState) -> str:
    """Create a concise analyst summary exclusively from existing outputs."""
    supplier_name = state.get("supplier_name", "The supplier")
    confidence_level = state.get("confidence_level", "low").title()
    completeness = state.get("completeness_results", [])
    gaps = state.get("gaps", [])
    scope3_level = (state.get("scope3_verdict") or {}).get(
        "level", "extraction_error"
    )

    scope3_positions = {
        "disclosed": "Scope 3 information appears usable as a preliminary input",
        "scope3_ready": "Scope 3 information appears usable as a preliminary input",
        "partial": "Scope 3 information is incomplete for decision use",
        "claim_only": "Scope 3 information is not yet usable for quantitative analysis",
        "materiality_claim": "the Scope 3 materiality position requires substantiation",
        "not_found": "Scope 3 information remains a material supplier-data gap",
        "extraction_error": "Scope 3 remains unassessed because extraction failed",
        "unassessed": "Scope 3 remains unassessed because extraction failed",
    }
    scope3_position = scope3_positions.get(
        scope3_level, "Scope 3 requires further source review"
    )

    coverage_text = "Environmental disclosure coverage was not quantified"

    if completeness:
        essential_total = sum(item.get("essential_total", 0) for item in completeness)
        essential_disclosed = sum(
            item.get("essential_disclosed", 0) + item.get("essential_partial", 0)
            for item in completeness
        )
        if essential_total:
            coverage_text = (
                f"The assessment located {essential_disclosed} of {essential_total} "
                "essential indicators, including partial disclosures"
            )

    critical_count = sum(gap.get("severity") == "critical" for gap in gaps)
    if gaps:
        gap_label = "gap" if len(gaps) == 1 else "gaps"
        gap_text = f"identified {len(gaps)} procurement-relevant disclosure {gap_label}"
        if critical_count:
            critical_label = "gap" if critical_count == 1 else "gaps"
            gap_text += f", including {critical_count} critical {critical_label}"
    else:
        gap_text = "identified no procurement-relevant disclosure gaps"

    review_text = ""
    if state.get("hitl_flag", False):
        review_text = " Human review is required before decision use."

    return (
        f"{supplier_name}'s uploaded BRSR was assessed with {confidence_level} "
        f"confidence. {coverage_text}; {scope3_position}, and the assessment "
        f"{gap_text}. Use the detailed gaps and supplier questions to guide targeted "
        f"follow-up; the confidence rating reflects assessment reliability, not ESG "
        f"performance.{review_text}"
    )


def _confidence_explanation(state: AssessmentState) -> str:
    """Return the rationale emitted by confidence scoring, with a safe fallback."""
    explanation = state.get("confidence_explanation")
    if explanation:
        return explanation

    level = state.get("confidence_level", "low").title()
    directive = state.get("confidence_directive", "").strip()
    if directive:
        return f"Overall confidence is {level}. {directive}"
    return f"Overall confidence is {level}; no further rationale is available."


def _procurement_recommendations(state: AssessmentState) -> list[dict]:
    """Link existing actions to their gap, finding basis, and source reference."""
    actions_by_gap = {
        action.get("gap_id"): action
        for action in state.get("recommended_actions", [])
        if action.get("gap_id")
    }
    questions_by_gap = {
        question.get("linked_gap_id") or question.get("gap_id"): question
        for question in state.get("followup_questions", [])
        if question.get("linked_gap_id") or question.get("gap_id")
    }
    recommendations = []

    for gap in state.get("gaps", []):
        gap_id = gap.get("gap_id")
        action = actions_by_gap.get(gap_id, {})
        recommendation = (action.get("action") or "").strip()
        if not recommendation:
            continue

        question = questions_by_gap.get(gap_id, {})
        basis = (
            question.get("basis")
            or gap.get("description")
            or gap.get("gap_name")
            or ""
        )
        recommendations.append(
            {
                "rank": gap.get("rank", action.get("rank", len(recommendations) + 1)),
                "gap_id": gap_id,
                "gap_name": gap.get("gap_name") or action.get("gap_name"),
                "severity": gap.get("severity"),
                "recommendation": recommendation,
                "basis": basis,
                "reference": format_reference(
                    gap.get("citation"), gap.get("brsr_reference")
                ),
            }
        )

    return recommendations


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
        executive_summary (first)
        disclaimer
        header: supplier_name, source_filename, assessment_id, timestamp,
                confidence_level, confidence_directive, hitl_flag
        completeness_assessment: completeness_results (from analysis_layer)
        scope3_verdict: (from analysis_layer)
        evidence_register: traceable extraction evidence and source locations
        gaps: (from analysis_layer)
        recommended_actions: (from analysis_layer)
        procurement_recommendations: actions linked to existing findings and references
        followup_questions: (from generate_questions)
        uncertain_fields: (from assess_confidence — used to render [⚠] markers)

    This node reads: ALL analysis and confidence fields
    This node writes: brief
    This node is the LAST node on the success path.
    """
    print(f"[compile_brief] Assembling ESG Intelligence Brief for: "
          f"{state['supplier_name']}")

    scope3_narrative = _scope3_assessment_narrative(state.get("scope3_verdict"))
    confidence_explanation = _confidence_explanation(state)
    procurement_recommendations = _procurement_recommendations(state)
    evidence_register = build_evidence_register(state)
    gap_references = {
        gap.get("gap_id", str(index)): format_reference(
            gap.get("citation"), gap.get("brsr_reference")
        )
        for index, gap in enumerate(state["gaps"], start=1)
    }
    question_references = {
        question.get("gap_id", str(index)): format_reference(
            question.get("reference") or question.get("citation")
        )
        for index, question in enumerate(state["followup_questions"], start=1)
    }

    brief = {
        "executive_summary": _executive_summary(state),
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
        "scope3_assessment_narrative": scope3_narrative,
        "confidence_explanation": confidence_explanation,
        "gaps": state["gaps"],
        "gap_references": gap_references,
        "recommended_actions": state["recommended_actions"],
        "procurement_recommendations": procurement_recommendations,
        "followup_questions": state["followup_questions"],
        "question_references": question_references,
        "uncertain_fields": state["uncertain_fields"],
        "extraction_errors": state["extraction_errors"],
        "evidence_register": evidence_register,
        "status": "brief_generated",
    }

    return {"brief": brief}

