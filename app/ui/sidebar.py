"""Sidebar rendering for the Streamlit UI."""

import streamlit as st


def render_sidebar() -> None:
    """Render application information and the current session status."""
    status_by_view = {
        "upload": "Ready",
        "processing": "Analysing...",
        "results": "Brief Ready",
    }
    view = st.session_state.get("view", "upload")
    status = status_by_view.get(view, "Ready")

    with st.sidebar:
        st.title("ESG Supplier Intelligence Agent")
        st.caption("v0.3")
        st.markdown(f"**Session Status:** {status}")

        with st.expander("How it Works"):
            st.write(
                "This application converts a BRSR filing into a procurement-ready "
                "ESG Intelligence Brief using Retrieval-Augmented Generation (RAG) "
                "and AI analysis."
            )

        with st.expander("About BRSR"):
            st.write(
                "BRSR (Business Responsibility and Sustainability Reporting) is "
                "SEBI's ESG disclosure framework for listed companies in India."
            )
