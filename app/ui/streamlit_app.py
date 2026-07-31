# app/ui/app.py

"""Streamlit entry point for the ESG Supplier Intelligence Agent."""

import streamlit as st

from app.ui.processing_view import render_processing_view
from app.ui.results_view import render_results_view
from app.ui.sidebar import render_sidebar
from app.ui.state import initialize_session_state
from app.ui.upload_view import render_upload_view


def main() -> None:
    """Configure and render the application for the current session view."""
    st.set_page_config(
        page_title="ESG Supplier Intelligence Agent",
        page_icon="🌱",
        layout="wide",
    )

    initialize_session_state()
    render_sidebar()

    view = st.session_state.get("view", "upload")

    if view == "upload":
        render_upload_view()
    elif view == "processing":
        render_processing_view()
    elif view == "results":
        render_results_view()
    else:
        st.error("Unknown application state.")


if __name__ == "__main__":
    main()
