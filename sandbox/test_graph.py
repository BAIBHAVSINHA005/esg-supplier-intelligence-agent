# sandbox/test_graph.py

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agent.graph import esg_graph
from app.agent.state import make_initial_state


def run(pdf_path: str = None):
    if pdf_path:
        pdf_bytes = Path(pdf_path).read_bytes()
        filename = Path(pdf_path).name
        supplier_name = filename.replace(".pdf", "").replace("_", " ").title()
        print(f"\nTesting with real PDF: {filename}")
    else:
        pdf_bytes = b""
        filename = "mock_test.pdf"
        supplier_name = "Mock Supplier Ltd"
        print("\nNo PDF provided — running with empty bytes (expect document failure)")

    state = make_initial_state(
        supplier_name=supplier_name,
        source_filename=filename,
        document_bytes=pdf_bytes,
    )

    result = esg_graph.invoke(state)

    print("\n" + "=" * 60)
    print("EXECUTION RESULT")
    print("=" * 60)
    print(f"Document failure:     {result.get('document_failure')}")
    print(f"Machine readable:     {result.get('is_machine_readable')}")
    print(f"BRSR section found:   {result.get('brsr_section_found')}")
    print(f"Confidence score:     {result.get('extraction_confidence_score')}")
    print(f"BRSR section length:  {len(result.get('brsr_section_text', '')):,} chars")

    if result.get("document_failure_reason"):
        print(f"Failure reason:       {result['document_failure_reason']}")

    brief = result.get("brief")
    if brief and not result.get("document_failure"):
        print(f"Brief generated:      Yes")
    elif result.get("error"):
        print(f"Error brief:          {result['error'][:100]}")

    print("=" * 60)


if __name__ == "__main__":
    pdf_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run(pdf_arg)