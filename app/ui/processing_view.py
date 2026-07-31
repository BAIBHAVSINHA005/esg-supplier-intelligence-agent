"""Processing view for the ESG report analysis flow."""

import streamlit as st


def render_processing_view() -> None:
    """Render the analysis-in-progress view."""
    st.title("Analysing ESG Report")
    st.write("Please wait while the ESG Intelligence Brief is being generated.")

    with st.spinner("Analysing report..."):
        pass
