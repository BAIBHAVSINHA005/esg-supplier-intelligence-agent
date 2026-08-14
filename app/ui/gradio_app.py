# app\ui\gradio_app.py

import gradio as gr
from pathlib import Path

from app.agent.evidence import format_reference
from app.services.supplier_assessment import run_supplier_assessment


def assess_supplier(pdf_file):

    if pdf_file is None:
        return "Please upload a PDF."

    pdf_path = Path(pdf_file)

    pdf_bytes = pdf_path.read_bytes()

    supplier_name = (
        pdf_path.stem
        .replace("_", " ")
        .title()
    )

    result = run_supplier_assessment(
        pdf_bytes=pdf_bytes,
        supplier_name=supplier_name,
        source_filename=pdf_path.name,
    )

    brief = result.get("brief", {})

    header = brief.get("header", {})

    scope3 = brief.get("scope3_verdict") or {}

    completeness = brief.get(
        "completeness_assessment",
        []
    )

    gaps = brief.get("gaps", [])

    questions = brief.get(
        "followup_questions",
        []
    )

    evidence_register = brief.get("evidence_register", [])

    scope3_evidence = next(
        (
            entry
            for entry in evidence_register
            if entry.get("indicator_id") == "e6_scope3_emissions"
        ),
        {},
    )

    report = []

    report.append("# ESG Supplier Intelligence Brief")

    report.append("\n## Executive Summary")

    report.append(
        brief.get(
            "executive_summary",
            "No executive summary is available for this assessment.",
        )
    )

    report.append(
        f"\nSupplier: {header.get('supplier_name', 'Unknown')}"
    )

    report.append(
        f"\nConfidence Level: "
        f"{header.get('confidence_level', 'unknown').upper()}"
    )

    report.append(
        f"\nHuman Review Required: "
        f"{header.get('hitl_flag', False)}"
    )

    report.append("\n## Confidence Explanation")

    report.append(
        brief.get(
            "confidence_explanation",
            header.get("confidence_directive", "No confidence explanation available."),
        )
    )

    report.append("\n---")

    # Scope 3

    report.append("\n## Scope 3 Verdict")

    report.append(
        scope3.get(
            "label",
            "No Scope 3 assessment available"
        )
    )

    report.append("\n### Scope 3 Assessment Narrative")

    report.append(
        brief.get(
            "scope3_assessment_narrative",
            "No Scope 3 assessment narrative is available.",
        )
    )

    evidence_status = scope3_evidence.get("evidence_status")
    if evidence_status == "not_found":
        report.append("No supporting evidence excerpt: Scope 3 was not found.")
    elif evidence_status == "extraction_error":
        report.append("No supporting evidence excerpt: extraction failed.")
    else:
        report.append(
            scope3_evidence.get("evidence_excerpt")
            or scope3.get("evidence", "No Scope 3 evidence excerpt is available.")
        )

    scope3_reference = format_reference(
        scope3_evidence.get("citation") or scope3.get("citation"),
        scope3_evidence.get("assessment_reference"),
    )
    report.append(f"Reference: {scope3_reference}")

    for location in scope3_evidence.get("source_locations", []):
        page = location.get("page", "unavailable")
        chunk_id = location.get("chunk_id")
        chunk_text = f", chunk {chunk_id}" if chunk_id else ""
        report.append(f"Matched source: page {page}{chunk_text}")

    report.append("\n## Evidence Register")

    for entry in evidence_register:
        reference = format_reference(
            entry.get("citation"), entry.get("assessment_reference")
        )
        sources = "; ".join(
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
        report.append(
            f"\n- {entry.get('indicator_name', entry.get('indicator_id', ''))}: "
            f"{entry.get('state', 'unknown')} | evidence status: "
            f"{entry.get('evidence_status', 'unknown')} | reference: {reference} | "
            f"matched sources: {sources}"
        )

    # Completeness

    report.append("\n---")

    report.append("\n## Completeness Assessment")

    for item in completeness:

        report.append(
            f"\nPrinciple {item['principle_number']} "
            f"({item['principle_name']})"
        )

        report.append(
            f"State: {item['state']}"
        )

        report.append(
            f"Essential Indicators: "
            f"{item['essential_disclosed']}/"
            f"{item['essential_total']} disclosed"
        )

    # Gaps

    report.append("\n---")

    report.append("\n## Critical Gaps")

    for gap in gaps:

        report.append(
            f"\n• {gap['gap_name']} — "
            f"{format_reference(gap.get('citation'), gap.get('brsr_reference'))}"
        )

    # Questions

    report.append("\n---")

    report.append("\n## Follow-Up Questions")

    for i, q in enumerate(questions, start=1):

        question_reference = format_reference(
            q.get("reference") or q.get("citation")
        )
        report.append(
            f"\n{i}. [{q.get('linked_gap_id', q.get('gap_id', ''))}] "
            f"{q['question']}\n   Reference: {question_reference}"
        )

    return "\n".join(report)


demo = gr.Interface(
    fn=assess_supplier,
    inputs=gr.File(
        label="Upload BRSR PDF"
    ),
    outputs=gr.Textbox(
        lines=30,
        label="ESG Assessment"
    ),
    title="ESG Supplier Intelligence Agent",
)

if __name__ == "__main__":
    demo.launch()
