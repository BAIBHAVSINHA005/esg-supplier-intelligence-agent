import gradio as gr
from pathlib import Path

from app.agent.graph import esg_graph
from app.agent.state import make_initial_state


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

    state = make_initial_state(
        supplier_name=supplier_name,
        source_filename=pdf_path.name,
        document_bytes=pdf_bytes,
    )

    result = esg_graph.invoke(state)

    brief = result.get("brief", {})

    header = brief.get("header", {})

    scope3 = brief.get("scope3_verdict", {})

    completeness = brief.get(
        "completeness_assessment",
        []
    )

    gaps = brief.get("gaps", [])

    questions = brief.get(
        "followup_questions",
        []
    )

    report = []

    report.append("# ESG Supplier Intelligence Brief")

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

    report.append("\n---")

    # Scope 3

    report.append("\n## Scope 3 Verdict")

    report.append(
        scope3.get(
            "label",
            "No Scope 3 assessment available"
        )
    )

    evidence = scope3.get("evidence", "")

    if len(evidence) > 150:
        evidence = evidence[:150] + "..."

    report.append(evidence)

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
            f"\n• {gap['gap_name']}"
        )

    # Questions

    report.append("\n---")

    report.append("\n## Follow-Up Questions")

    for i, q in enumerate(questions, start=1):

        report.append(
            f"\n{i}. {q['question']}"
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