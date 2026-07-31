"""Upload view for starting an ESG report analysis."""

import streamlit as st


def render_upload_view() -> None:
    """Render the supplier and BRSR report upload form."""
    st.title("ESG Supplier Intelligence Agent")
    st.write("Upload a BRSR report to generate an ESG Intelligence Brief.")

    supplier_name = st.text_input(
        "Supplier Name (optional)",
        value=st.session_state.supplier_name,
    )
    uploaded_file = st.file_uploader("Upload BRSR Report", type=["pdf"])

    st.session_state.supplier_name = supplier_name
    st.session_state.uploaded_file = uploaded_file

    if st.button("Analyse Report"):
        if uploaded_file is None:
            st.error("Please upload a BRSR report.")
        else:
            st.session_state.view = "processing"
