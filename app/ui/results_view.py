"""Results view for the ESG Intelligence Brief."""

import streamlit as st


def render_results_view() -> None:
    """Render the completed ESG Intelligence Brief."""
    analysis_result = st.session_state.analysis_result or {}
    brief = analysis_result.get("brief", {})
    header = brief.get("header", {})
    scope3_verdict = brief.get("scope3_verdict") or {}
    extraction_errors = brief.get("extraction_errors", [])

    st.title("ESG Intelligence Brief")
    st.success("Analysis completed successfully.")

    supplier_column, confidence_column, hitl_column = st.columns(3)
    supplier_column.metric("Supplier Name", header.get("supplier_name", "Unknown"))
    confidence_column.metric(
        "Confidence Level",
        header.get("confidence_level", "unknown").upper(),
    )
    hitl_flag = header.get("hitl_flag", False)
    hitl_column.metric("HITL Flag", "Yes" if hitl_flag else "No")

    if hitl_flag:
        st.warning("Human review is required before acting on this brief.")

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

    st.subheader("Scope 3 Verdict")
    st.info(scope3_verdict.get("label", "No Scope 3 assessment available."))

    st.subheader("Scope 3 Evidence")
    st.info(scope3_verdict.get("evidence", "No Scope 3 evidence available."))

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
                    "Description": gap.get("description", ""),
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
                    "Question": question.get("question", ""),
                }
                for question in questions
            ]
        )
    else:
        st.info("No follow-up questions are available.")
