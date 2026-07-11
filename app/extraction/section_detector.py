# app/extraction/section_detector.py

# Markers that signal the start of a BRSR chapter.
# Listed in rough order of specificity — the more specific, the better.
BRSR_START_MARKERS = [
    "business responsibility and sustainability report",
    "business responsibility & sustainability report",
    "section a: general disclosures",
    "section a : general disclosures",
    "national guidelines on responsible business conduct",
    "principle-wise performance disclosure",
    "principle wise performance disclosure",
]

# Markers that appear in the body of a BRSR.
# Used to CONFIRM a section is actually a BRSR after the start marker is found.
# Prevents false positives from casual BRSR mentions in other chapters.
BRSR_BODY_MARKERS = [
    "section b: management and process",
    "section c: principle wise",
    "section b : management",
    "principle 6",
    "scope 1",
    "scope 2",
    "ghg emissions",
    "greenhouse gas",
]

# Principle 6 (Environment) specific markers
# This principle contains the emissions data critical to our use case
PRINCIPLE_6_MARKERS = [
    "principle 6",
    "scope 1",
    "scope 2",
    "ghg emission",
    "greenhouse gas",
    "energy consumption",
    "renewable energy",
]


def find_brsr_section(full_text: str) -> tuple[bool, str, int]:
    """
    Locate the BRSR chapter within a full annual report.

    Strategy:
    1. Search for the earliest BRSR start marker in the document
    2. Extract a 60,000-character window forward from that position
    3. Confirm the extraction is a real BRSR by checking for body markers
    4. Require at least 2 body markers to avoid false positives

    Returns:
        found           — True if a BRSR section was confidently located
        section_text    — extracted text (empty string if not found)
        start_index     — character position of the BRSR start (-1 if not found)

    Tuning note:
    If real BRSR filings are being missed, add their specific section headers
    to BRSR_START_MARKERS and test again. The 60,000-char window covers most
    BRSR chapters (typically 30–70 pages = 40,000–80,000 chars).
    Increase to 80,000 if long filings are being truncated.
    """
    lower_text = full_text.lower()

    # Find the earliest occurrence of any start marker
    start_idx = None
    for marker in BRSR_START_MARKERS:
        idx = lower_text.find(marker)
        if idx != -1:
            if start_idx is None or idx < start_idx:
                start_idx = idx

    if start_idx is None:
        return False, "", -1

    # Extract a window forward from the start marker
    section_text = full_text[start_idx: start_idx + 60000]
    section_lower = section_text.lower()

    # Confirm with body markers — require at least 2 to avoid false positives
    body_marker_count = sum(1 for m in BRSR_BODY_MARKERS if m in section_lower)
    if body_marker_count < 2:
        return False, "", -1

    return True, section_text, start_idx


def has_principle_6_content(brsr_section_text: str) -> bool:
    """
    Check whether the BRSR section contains Principle 6 (Environment) data.
    Principle 6 is the most critical section for our Scope 3 assessment.
    Requires at least 2 markers to avoid false positives.
    """
    lower = brsr_section_text.lower()
    count = sum(1 for m in PRINCIPLE_6_MARKERS if m in lower)
    return count >= 2


def compute_confidence_score(
    readable: bool,
    brsr_found: bool,
    section_length: int,
    has_p6: bool
) -> float:
    """
    Weighted confidence score 0.0–1.0 based on four document quality checks.

    Weights reflect importance to downstream extraction quality:
    - Readable:           0.40  (scanned PDF = nothing else matters)
    - BRSR found:         0.35  (cannot extract without the section)
    - Section substantial: 0.15 (short section = likely partial extraction)
    - P6 present:         0.10  (critical for Scope 3 use case)
    """
    score = 0.0
    if readable:
        score += 0.40
    if brsr_found:
        score += 0.35
    if section_length > 10000:
        score += 0.15
    if has_p6:
        score += 0.10
    return round(score, 2)


def score_to_level(score: float) -> str:
    """Convert a 0.0–1.0 score to a named confidence level."""
    if score >= 0.80:
        return "high"
    elif score >= 0.50:
        return "medium"
    else:
        return "low"