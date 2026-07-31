# app/ui/state.py

"""Streamlit session-state initialization for the UI."""

import streamlit as st


def initialize_session_state() -> None:
    """Initialize UI session-state values when they are not already set."""
    defaults = {
        "view": "upload",
        "uploaded_file": None,
        "supplier_name": "",
        "analysis_result": None,
        "is_processing": False,
        "error_message": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
