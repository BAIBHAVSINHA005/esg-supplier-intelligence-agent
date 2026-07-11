# app/agent/nodes/quality.py

from app.agent.state import AssessmentState


def quality_check(state: AssessmentState) -> dict:
    """
    PHASE 2 PLACEHOLDER — Real implementation in Phase 2 (Day 5).

    Real responsibility:
    - Check if document_text is long enough to be machine-readable
      (chars_per_page < 200 → likely scanned → is_machine_readable = False)
    - Search document_text for BRSR section markers
      ("business responsibility and sustainability report", "brsr", "ngrbc", etc.)
    - Extract brsr_section_text by slicing from the marker forward
    - Calculate extraction_confidence_score from readability + section detection
    - Set document_failure = True if is_machine_readable=False OR brsr_section_found=False

    This node does NOT call Claude.
    This node does NOT touch ChromaDB.
    This node only analyses the extracted text from ingest_document.

    CRITICAL: document_failure is the ONLY field that drives routing.
    route_after_quality_check reads this field to decide the next node.
    Set it accurately — it determines whether the rest of the pipeline runs.
    """
    print(f"[quality_check] PLACEHOLDER — would assess document quality for: {state['source_filename']}")

    return {
        "is_machine_readable": True,
        "brsr_section_found": True,
        "brsr_section_text": "PLACEHOLDER: BRSR section text will appear here.",
        "extraction_confidence_score": 0.9,
        "document_failure": False,
        "document_failure_reason": None,
    }

