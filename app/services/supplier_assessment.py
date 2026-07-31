# app/services/supplier_assessment.py
"""Service for running the supplier ESG assessment workflow."""

from typing import Any

from app.agent.graph import esg_graph
from app.agent.state import make_initial_state


def run_supplier_assessment(
    pdf_bytes: bytes,
    supplier_name: str,
    source_filename: str,
) -> dict[str, Any]:
    """Run the ESG assessment workflow and return its structured result."""
    state = make_initial_state(
        supplier_name=supplier_name,
        source_filename=source_filename,
        document_bytes=pdf_bytes,
    )

    return esg_graph.invoke(state)
