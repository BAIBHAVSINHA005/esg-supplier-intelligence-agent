"""Results view for the ESG Intelligence Brief."""

import streamlit as st

from app.agent.evidence import format_reference


def _source_locations_text(entry: dict) -> str:
    return "; ".join(
        (
            f"page {location.get('page')}"
            if location.get("page") is not None
            else "page unavailable"
        )
        + (
            f" / chunk {location.get('chunk_id')}"
            if location.get("chunk_id")
            else ""
        )
        for location in entry.get("source_locations", [])
    ) or "—"


def render_results_view() -> None:
    """Render the completed ESG Intelligence Brief."""
    analysis_result = st.session_state.analysis_result or {}
    brief = analysis_result.get("brief", {})
    header = brief.get("header", {})
    scope3_verdict = brief.get("scope3_verdict") or {}
    extraction_errors = brief.get("extraction_errors", [])
    evidence_register = brief.get("evidence_register", [])
    scope3_evidence = next(
        (
            entry
            for entry in evidence_register
            if entry.get("indicator_id") == "e6_scope3_emissions"
        ),
        {},
    )

    st.title("ESG Intelligence Brief")
    st.success("Analysis completed successfully.")

    st.subheader("Executive Summary")
    st.write(
        brief.get(
            "executive_summary",
            "No executive summary is available for this assessment.",
        )
    )

    supplier_column, confidence_column, hitl_column = st.columns(3)
    supplier_column.metric("Supplier Name", header.get("supplier_name") or "Unknown")
    confidence_column.metric(
        "Confidence Level",
        header.get("confidence_level", "unknown").upper(),
    )
    hitl_flag = header.get("hitl_flag", False)
    hitl_column.metric("HITL Flag", "Yes" if hitl_flag else "No")

    if hitl_flag:
        st.warning("Human review is required before acting on this brief.")

    st.subheader("Confidence Explanation")
    st.info(
        brief.get(
            "confidence_explanation",
            header.get("confidence_directive", "No confidence explanation available."),
        )
    )

    if extraction_errors:
        st.warning(
            "Some indicators could not be assessed because extraction failed. "
            "They are not treated as missing disclosures."
        )
        st.table(
            [
                {
                    "Indicator": error.get(
                        "indicator_name", error.get("indicator_id", "")
                    ),
                    "Error": error.get("error_code", "extraction_error"),
                }
                for error in extraction_errors
            ]
        )

    st.subheader("Scope 3 Assessment")
    st.info(scope3_verdict.get("label", "No Scope 3 assessment available."))
    st.write(
        brief.get(
            "scope3_assessment_narrative",
            "No Scope 3 assessment narrative is available.",
        )
    )

    st.subheader("Procurement Recommendations")
    recommendations = brief.get("procurement_recommendations", [])
    if recommendations:
        st.table(
            [
                {
                    "Rank": item.get("rank", ""),
                    "Gap": item.get("gap_name", item.get("gap_id", "")),
                    "Severity": item.get("severity", ""),
                    "Recommendation": item.get("recommendation", ""),
                    "Finding basis": item.get("basis", ""),
                }
                for item in recommendations
            ]
        )
    else:
        st.info("No procurement recommendations are required from the identified gaps.")

    st.subheader("Completeness Assessment")
    completeness = brief.get("completeness_assessment", [])
    if completeness:
        st.table(
            [
                {
                    "Principle": (
                        f"{item.get('principle_number', '')}: "
                        f"{item.get('principle_name', '')}"
                    ),
                    "State": item.get("state", "unknown"),
                    "Essential Indicators": (
                        f"{item.get('essential_disclosed', 0)}/"
                        f"{item.get('essential_total', 0)} disclosed"
                    ),
                }
                for item in completeness
            ]
        )
    else:
        st.info("No completeness assessment is available.")

    st.subheader("Critical Gaps")
    gaps = brief.get("gaps", [])
    if gaps:
        st.table(
            [
                {
                    "Gap": gap.get("gap_name", ""),
                    "Severity": gap.get("severity", ""),
                    "Why it matters": gap.get("description", ""),
                }
                for gap in gaps
            ]
        )
    else:
        st.info("No critical gaps were identified.")

    st.subheader("Follow-up Questions")
    questions = brief.get("followup_questions", [])
    if questions:
        st.table(
            [
                {
                    "Rank": question.get("rank", ""),
                    "Gap": question.get("linked_gap_id", question.get("gap_id", "")),
                    "Question": question.get("question", ""),
                }
                for question in questions
            ]
        )
    else:
        st.info("No follow-up questions are available.")

    with st.expander("Evidence Details"):
        st.markdown("#### Scope 3 Evidence")
        scope3_status = scope3_evidence.get("evidence_status")
        if scope3_status == "not_found":
            st.info(
                "No supporting evidence excerpt is available because Scope 3 was not found."
            )
        elif scope3_status == "extraction_error":
            st.warning(
                "No supporting evidence excerpt is available because extraction failed."
            )
        else:
            st.info(
                scope3_evidence.get("evidence_excerpt")
                or scope3_verdict.get("evidence")
                or "No Scope 3 evidence excerpt is available."
            )

        scope3_reference = format_reference(
            scope3_evidence.get("citation") or scope3_verdict.get("citation"),
            scope3_evidence.get("assessment_reference"),
        )
        st.caption(f"Reference: {scope3_reference}")
        if scope3_evidence.get("source_locations"):
            st.caption(f"Matched source: {_source_locations_text(scope3_evidence)}")

        st.markdown("#### Indicator Evidence Register")
        if evidence_register:
            st.table(
                [
                    {
                        "Indicator": entry.get(
                            "indicator_name", entry.get("indicator_id", "")
                        ),
                        "State": entry.get("state", "unknown"),
                        "Evidence status": entry.get("evidence_status", "unknown"),
                        "Evidence excerpt": entry.get("evidence_excerpt") or "—",
                        "Reference": format_reference(
                            entry.get("citation"), entry.get("assessment_reference")
                        ),
                        "Matched sources": _source_locations_text(entry),
                    }
                    for entry in evidence_register
                ]
            )
        else:
            st.info("No indicator-level evidence metadata is available.")

        st.markdown("#### Finding and Question References")
        reference_rows = [
            {
                "Item": item.get("gap_id", ""),
                "Type": "Gap",
                "Reference": format_reference(
                    item.get("citation"), item.get("brsr_reference")
                ),
            }
            for item in gaps
        ] + [
            {
                "Item": item.get("linked_gap_id", item.get("gap_id", "")),
                "Type": "Follow-up question",
                "Reference": format_reference(
                    item.get("reference") or item.get("citation")
                ),
            }
            for item in questions
        ]
        if reference_rows:
            st.table(reference_rows)
        else:
            st.info("No finding or question references are available.")
