"""Processing view for the ESG report analysis flow."""

import streamlit as st

from app.services.supplier_assessment import run_supplier_assessment


def render_processing_view() -> None:
    """Render the analysis-in-progress view."""
    st.title("Analysing ESG Report")
    st.write("Please wait while the ESG Intelligence Brief is being generated.")

    with st.spinner("Analysing report..."):
        try:
            uploaded_file = st.session_state.uploaded_file
            supplier_name = st.session_state.supplier_name

            result = run_supplier_assessment(
                pdf_bytes=uploaded_file.getvalue(),
                supplier_name=supplier_name,
                source_filename=uploaded_file.name,
            )

            st.session_state.analysis_result = result
            st.session_state.view = "results"
            st.rerun()
        except Exception as error:
            st.session_state.error_message = str(error)
            st.session_state.view = "upload"
            st.rerun()
