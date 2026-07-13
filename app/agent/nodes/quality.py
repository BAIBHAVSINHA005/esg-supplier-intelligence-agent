# app/agent/nodes/quality.py




from app.agent.state import AssessmentState
from app.extraction.pdf_parser import chars_per_page, is_machine_readable
from app.extraction.section_detector import (
    find_brsr_section,
    has_principle_6_content,
    compute_confidence_score,
    
)



def quality_check(state: AssessmentState) -> dict:
    """
    Node 2: Assess document quality and locate the BRSR section.

    Reads:  document_text, num_pages, document_failure (from ingest)
    Writes: is_machine_readable, brsr_section_found, brsr_section_text,
            extraction_confidence_score, document_failure, document_failure_reason

    Does NOT write confidence_level, confidence_directive, or hitl_flag.
    Those are written by assess_confidence.
    Does NOT call LLMs.

    Routing: If document_failure is True after this node,
             route_after_quality_check sends execution to handle_failure.
    """
    print("[quality_check]")

    # If ingest already failed, pass through — do not overwrite the failure reason
    if state.get("document_failure", False):
        print("[quality_check] Upstream failure detected — skipping quality check")
        return {}

    full_text = state["document_text"]
    num_pages = state["num_pages"]

    # Check 1: Machine readability
    avg_chars = chars_per_page(full_text, num_pages)
    readable = is_machine_readable(avg_chars)
    print(f"[quality_check] {avg_chars:.0f} chars/page — readable: {readable}")

    # Check 2: Locate BRSR section
    brsr_found, brsr_text, start_idx = find_brsr_section(full_text)

    

    # Check 3: Principle 6 presence
    has_p6 = has_principle_6_content(brsr_text) if brsr_found else False
    print(f"[quality_check] Principle 6 content present: {has_p6}")

    # Compute raw confidence score
    score = compute_confidence_score(
        readable=readable,
        brsr_found=brsr_found,
        section_length=len(brsr_text),
        has_p6=has_p6,
    )
    print(f"[quality_check] Confidence score: {score}")

    # Determine failure conditions
    failure = not readable or not brsr_found
    failure_reason = None

    if not readable:
        failure_reason = (
            f"Document appears to be scanned or image-based "
            f"({avg_chars:.0f} extractable characters per page; minimum is 200). "
            f"Text extraction is not possible. Please provide a machine-readable PDF."
        )
    elif not brsr_found:
        failure_reason = (
            "BRSR section could not be located in the uploaded document. "
            "Please ensure this is a BRSR filing or an annual report "
            "containing a BRSR chapter."
        )

    return {
        "is_machine_readable": readable,
        "brsr_section_found": brsr_found,
        "brsr_section_text": brsr_text,
        "extraction_confidence_score": score,
        "document_failure": failure,
        "document_failure_reason": failure_reason,
    }