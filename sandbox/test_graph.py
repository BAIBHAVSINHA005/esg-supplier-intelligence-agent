# sandbox/test_graph.py

import sys
from pathlib import Path
from pprint import pprint



sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agent.graph import esg_graph
from app.agent.state import make_initial_state


def print_extraction_summary(result: dict) -> None:
    """Print a compact extraction summary from the full graph result."""
    extracted = result.get("extracted_indicators", {})
    p6 = extracted.get("principle_6", {})

    if not p6:
        print("  extracted_indicators: empty (placeholder or upstream failure)")
        return

    counts = {}
    for r in p6.values():
        s = r.get("state", "unknown")
        counts[s] = counts.get(s, 0) + 1

    # This is to ensure that we get High-level summary
    # Per-indicator visibility
    # Scope 3 diagnostics

    # all in one place.
    print("\n  Indicator detail:")

    for ind_id, ind_result in p6.items():
        state_val = ind_result.get("state", "unknown")
        method = ind_result.get("extraction_method", "?")

        print(f"    {ind_id}: " f"{state_val} " f"[{method}]")

    icons = {"disclosed": "✅", "partially_disclosed": "⚠️", "not_found": "❌"}
    print(f"  Principle 6 indicators ({len(p6)} total):")
    for state_name, count in counts.items():
        icon = icons.get(state_name, "?")
        print(f"    {icon} {state_name.replace('_', ' ').title()}: {count}")

    # Scope 3 quick view
    scope3 = p6.get("e6_scope3_emissions", {})
    if scope3:
        print(f"  Scope 3 state:       {scope3.get('state', 'unknown')}")
        print(f"  Scope 3 mentioned:   {scope3.get('scope3_mentioned', False)}")
        print(
            f"  Absolute number:     {scope3.get('scope3_has_absolute_number', False)}"
        )
        print(f"  Methodology found:   {scope3.get('scope3_has_methodology', False)}")


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

    print("\nANALYSIS OBJECTS")


    print("=" * 60)

    print("\nScope3 Verdict")
    print(result.get("scope3_verdict"))

    print("\nCompleteness Results")
    print(result.get("completeness_results"))

    print("\nGaps")
    for gap in result.get("gaps", []):
        print(gap)

    print("\nCONFIDENCE OBJECT")
    print("=" * 60)

    print("\nLevel:")
    print(result.get("confidence_level"))

    print("\nDirective:")
    print(result.get("confidence_directive"))

    print("\nHITL:")
    print(result.get("hitl_flag"))

    print("\nUncertain Fields:")
    print(result.get("uncertain_fields"))

    print("\nEXTRACTED INDICATORS:")
    print_extraction_summary(result)
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

    print("\nFOLLOW-UP QUESTIONS")
    print("=" * 60)

    for q in result.get("followup_questions", []):
        print(f"\n[{q['rank']}] {q['gap_id']}")
        print(q["question"])
    
#debugging
    print("\nBRIEF OBJECT")
    print("=" * 60)

    pprint(result.get("brief"))


    print("\nFIRST 3000 CHARS OF BRSR SECTION")
    print("=" * 60)

    print(
    result.get("brsr_section_text", "")[:3000]
    )


if __name__ == "__main__":
    pdf_arg = sys.argv[1] if len(sys.argv) > 1 else None
    run(pdf_arg)
