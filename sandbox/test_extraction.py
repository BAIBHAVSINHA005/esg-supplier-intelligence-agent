# sandbox/test_extraction.py
#
# Standalone test for the extract_indicators node.
# Runs ingest → quality_check → extract_indicators without LangGraph overhead.
# Prints detailed per-indicator results.
#
# Usage:
#   python sandbox/test_extraction.py path/to/brsr.pdf

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agent.state import make_initial_state
from app.agent.nodes.ingest import ingest_document
from app.agent.nodes.quality import quality_check
from app.agent.nodes.extract import extract_indicators


STATE_COLOURS = {
    "disclosed":          "✅",
    "partially_disclosed": "⚠️ ",
    "not_found":          "❌",
}


def print_indicator_result(indicator_id: str, result: dict) -> None:
    icon = STATE_COLOURS.get(result.get("state", ""), "?")
    state = result.get("state", "unknown").replace("_", " ").upper()
    value = result.get("value", "")
    confidence = result.get("confidence", 0.0)
    evidence = result.get("evidence", "")
    method = result.get("extraction_method", "?")

    print(f"\n  {icon} {indicator_id}")
    print(f"     State:      {state}")
    print(f"     Method:     {method}  |  Confidence: {confidence:.2f}")
    if value:
        print(f"     Value:      {value}")
    if evidence:
        # Truncate long evidence for display
        short = evidence.replace("\n", " ").strip()[:200]
        print(f"     Evidence:   {short}...")

    # Scope 3 specific metadata
    scope3_fields = [
        ("scope3_mentioned",              "Mentioned"),
        ("scope3_has_absolute_number",    "Absolute number"),
        ("scope3_has_methodology",        "Methodology named"),
        ("scope3_is_intensity_only",      "Intensity only"),
        ("scope3_has_materiality_claim",  "Materiality claim"),
    ]
    scope3_meta = {k: result.get(k) for k, _ in scope3_fields if k in result}
    if scope3_meta:
        print(f"     Scope3 signals:")
        for key, label in scope3_fields:
            if key in result:
                print(f"       {label}: {result[key]}")


def run(pdf_path: str) -> None:
    path = Path(pdf_path)
    if not path.exists():
        print(f"ERROR: File not found: {pdf_path}")
        sys.exit(1)

    print(f"\n{'='*65}")
    print(f" EXTRACTION TEST: {path.name}")
    print(f"{'='*65}")

    # Build initial state
    pdf_bytes = path.read_bytes()
    state = make_initial_state(
        supplier_name=path.stem.replace("_", " ").title(),
        source_filename=path.name,
        document_bytes=pdf_bytes,
    )

    # Run nodes manually (no LangGraph graph overhead)
    print("\n[1/3] Ingesting document...")
    state.update(ingest_document(state))
    print(f"      Pages: {state['num_pages']}  |  Chars: {len(state['document_text']):,}")

    if state.get("document_failure"):
        print(f"\nDOCUMENT FAILURE: {state['document_failure_reason']}")
        return

    print("\n[2/3] Quality check...")
    state.update(quality_check(state))
    print(f"      Machine readable:   {state['is_machine_readable']}")
    print(f"      BRSR section found: {state['brsr_section_found']}")
    print(f"      Section length:     {len(state['brsr_section_text']):,} chars")
    print(f"      Confidence score:   {state['extraction_confidence_score']}")

    if state.get("document_failure"):
        print(f"\nQUALITY FAILURE: {state['document_failure_reason']}")
        return

    print("\n[3/3] Extracting indicators...")
    state.update(extract_indicators(state))

    extracted = state.get("extracted_indicators", {})
    p6 = extracted.get("principle_6", {})

    if not p6:
        print("\n  No indicators extracted.")
        return

    # Summary counts
    counts = {}
    for r in p6.values():
        s = r.get("state", "unknown")
        counts[s] = counts.get(s, 0) + 1

    print(f"\n{'='*65}")
    print(f" RESULTS — PRINCIPLE 6 ({len(p6)} indicators)")
    print(f"{'='*65}")
    print(f"  ✅ Disclosed:           {counts.get('disclosed', 0)}")
    print(f"  ⚠️  Partially disclosed: {counts.get('partially_disclosed', 0)}")
    print(f"  ❌ Not found:           {counts.get('not_found', 0)}")

    print(f"\n{'-'*65}")
    print(" INDICATOR DETAIL")
    print(f"{'-'*65}")
    for indicator_id, result in p6.items():
        print_indicator_result(indicator_id, result)

    print(f"\n{'='*65}")
    print(" SCOPE 3 CLASSIFICATION SIGNALS (for analysis_layer)")
    print(f"{'='*65}")
    scope3 = p6.get("e6_scope3_emissions", {})
    if scope3:
        print(f"  State:              {scope3.get('state', 'unknown')}")
        print(f"  Mentioned:          {scope3.get('scope3_mentioned', False)}")
        print(f"  Absolute number:    {scope3.get('scope3_has_absolute_number', False)}")
        print(f"  Methodology named:  {scope3.get('scope3_has_methodology', False)}")
        print(f"  Intensity only:     {scope3.get('scope3_is_intensity_only', False)}")
        print(f"  Materiality claim:  {scope3.get('scope3_has_materiality_claim', False)}")
    else:
        print("  Scope 3 indicator not found in results")

    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sandbox/test_extraction.py path/to/brsr.pdf")
        sys.exit(1)
    run(sys.argv[1])