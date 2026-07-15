# app/agent/nodes/extract.py

from app.agent.state import AssessmentState
from app.schemas.loader import load_schema, get_indicators
from app.extraction.keyword_extractor import extract_principle_indicators


def extract_indicators(state: AssessmentState) -> dict:
    """
    Node 3: Extract ESG indicator data from the BRSR section text.

    Phase 3 implementation — deterministic keyword extraction only.
    No LLM calls. No ChromaDB. No API costs.

    Reads:  brsr_section_text, document_failure
    Writes: extracted_indicators

    extracted_indicators structure:
        {
            "principle_6": {
                "e6_scope1_emissions": {
                    "indicator_id": str,
                    "state": "disclosed" | "partially_disclosed" | "not_found",
                    "value": str,      # extracted value or empty string
                    "evidence": str,   # text snippet justifying the classification
                    "citation": str,   # BRSR indicator reference or "Not found..." text
                    "extraction_method": "keyword",  # Phase 4 will write "llm"
                    "confidence": float,  # 0.0 – 1.0
                    "uncertain": bool,    # True for all keyword extractions
                },
                ...
            }
        }

    Phase 4 changes to this node:
    - Add ChromaDB retrieval for indicator context before each extraction
    - Add Claude call per indicator (or batched) to replace keyword logic
    - Keep the same output structure — downstream nodes must not change
    """
    print("[extract_indicators]")

    # If upstream nodes failed, skip extraction
    if state.get("document_failure", False):
        print("[extract_indicators] Upstream document failure — skipping extraction")
        return {"extracted_indicators": {}}

    brsr_text = state.get("brsr_section_text", "")




    if not brsr_text:
        print("[extract_indicators] WARNING: brsr_section_text is empty")
        return {"extracted_indicators": {}}

    print(f"[extract_indicators] Extracting from {len(brsr_text):,} char BRSR section")

    # Load schema — cached after first call
    schema = load_schema("brsr_v2023")

    # Phase 3: extract Principle 6 only
    # Phase 4+: expand to all principles using get_all_principle_ids(schema)
    principle_6_indicators = get_indicators(schema, "principle_6")

    print(f"[extract_indicators] Running keyword extraction for {len(principle_6_indicators)} indicators")

    principle_6_results = extract_principle_indicators(
        principle_indicators=principle_6_indicators,
        brsr_section_text=brsr_text,
    )

    #print only 1 indicator result for debugging


   

    # Count results by state for logging
    state_counts = {}
    for result in principle_6_results.values():
        s = result.get("state", "unknown")
        state_counts[s] = state_counts.get(s, 0) + 1

    print(f"[extract_indicators] Results: {state_counts}")

    
     
    
    return {
        "extracted_indicators": {
            "principle_6": principle_6_results
        }
    }