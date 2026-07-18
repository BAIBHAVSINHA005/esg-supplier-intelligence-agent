## File 3 — `app/extraction/keyword_extractor.py` (create)


# app/extraction/keyword_extractor.py
#
# Deterministic keyword-based extraction for BRSR indicators.
# Phase 3 implementation — no LLMs, no ChromaDB, no API calls.
#
# Design decisions:
# - All results carry extraction_method="keyword" and uncertain=True.
#   Phase 4 LLM extraction will overwrite these.
# - Scope 3 indicator carries extra metadata fields needed by scope3_classifier.
# - Value extraction grabs a context snippet, not a parsed number.
#   Exact value parsing is Phase 4 work.
# - Search is performed on the full brsr_section_text, not chunked.
#   Chunking is a Phase 4 concern for RAG retrieval.

import re
from typing import Optional

# ---------------------------------------------------------------------------
# KEYWORD DEFINITIONS
# Maps indicator_id → list of search terms (all searched case-insensitively).
# Order matters: more specific terms first.
# ---------------------------------------------------------------------------

INDICATOR_KEYWORDS: dict[str, list[str]] = {
    "e6_energy_consumption": [
        "energy consumption",
        "total energy",
        "energy used",
        "energy use",
        "gigajoule",
        "terajoule",
        "gj consumed",
    ],
    "e6_scope1_emissions": [
        "scope 1",
        "scope-1",
        "scope i emission",
        "direct emission",
        "direct ghg",
        "direct greenhouse gas",
    ],
    "e6_scope2_emissions": [
        "scope 2",
        "scope-2",
        "scope ii emission",
        "indirect emission",
        "energy indirect",
        "purchased electricity emission",
    ],
    "e6_ghg_methodology": [
        "ghg protocol",
        "greenhouse gas protocol",
        "iso 14064",
        "ipcc",
        "corporate value chain standard",
        "scope 3 evaluator",
        "emission factor",
        "global warming potential",
        "gwp",
    ],
    "e6_ghg_intensity": [
        "ghg intensity",
        "emission intensity",
        "co2 intensity",
        "carbon intensity",
        "tco2e per",
        "per unit of revenue",
        "per crore",
        "per tonne of production",
        "Energy intensity",
        "emission per unit",
    ],
    "e6_scope3_emissions": [
        "scope 3",
        "scope-3",
        "scope iii",
        "value chain emission",
        "upstream emission",
        "downstream emission",
        "other indirect emission",
        "purchased goods",  # Scope 3 Category 1 signals
        "business travel emission",
        "employee commuting",
    ],
    "e6_climate_target": [
        "net zero",
        "net-zero",
        "net carbon zero",
        "net carbon neutrality",
        "carbon neutral",
        "carbon neutrality",
        "emission reduction target",
        "climate target",
        "decarbonisation target",
        "decarbonization target",
        "sbti",
        "science based target",
        "science-based target",
        "carbon negative",
        "reduce emission",
        "decarbonization target",
        "emission reduction goal",
    ],
    "e6_water_consumption": [
        "water withdrawal",
        "water consumption",
        "water used",
        "water usage",
        "water discharge",
        "kilolitre",
        "water intensity",
    ],
    "e6_waste_generated": [
        "waste generated",
        "total waste",
        "hazardous waste",
        "non-hazardous waste",
        "waste disposed",
        "waste management",
        "waste diverted",
    ],
}

# Phrases that suggest an indicator is explicitly not being disclosed
ABSENCE_PHRASES: list[str] = [
    "not applicable",
    "not assessed",
    "not reported",
    "not measured",
    "not tracked",
    "not calculated",
    "not available",
    "data not available",
    "under evaluation",
    "being evaluated",
    "currently assessing",
    "will be reported",
]

# Scope 3 specific: phrases that suggest a formal materiality claim
SCOPE3_MATERIALITY_PHRASES: list[str] = [
    "scope 3 is not material",
    "scope 3 is not applicable",
    "scope 3 not applicable",
    "scope 3 not assessed",
    "scope 3 not relevant",
    "scope 3 emissions are not",
    "not material to our operations",
    "not applicable to our business",
]

# Pattern to detect GHG emission numbers near a keyword
# Looks for: optional leading text, a number, and a unit
# Examples matched: "12,450 tCO2e", "1.2 million tCO2e", "23,456 MT CO2e"
GHG_NUMBER_RE = re.compile(
    r"([\d,]+(?:\.\d+)?)"  # The number itself (with optional commas/decimals)
    r"\s*"  # Optional whitespace
    r"(?:million\s+)?"  # Optional "million" qualifier
    r"(?:"
    r"tco2[\s-]?e"  # tCO2e, tCO2-e
    r"|mt\s*co2[\s-]?e"  # MT CO2e
    r"|mtco2e"  # mtCO2e (no spaces)
    r"|ktco2e"  # ktCO2e
    r"|metric\s+tonne.*?co2"  # metric tonnes of CO2...
    r"|tonne.*?co2.*?equiv"  # tonnes CO2 equivalent
    r"|co2\s*equivalent"  # CO2 equivalent
    r")",
    re.IGNORECASE,
)

# Context window size: chars to extract around a keyword match
# Large enough to capture the full data row but not so large that unrelated
# numbers are included.
CONTEXT_WINDOW = 400


# ---------------------------------------------------------------------------
# CORE EXTRACTION FUNCTIONS
# ---------------------------------------------------------------------------


def find_keyword_positions(text: str, keywords: list[str]) -> list[tuple[int, str]]:
    """
    Find all positions of any keyword in the text (case-insensitive).

    Returns:
        List of (position, matched_keyword) sorted by position.
        Empty list if no keywords found.
    """
    lower_text = text.lower()
    matches = []
    for keyword in keywords:
        idx = 0
        while True:
            pos = lower_text.find(keyword.lower(), idx)
            if pos == -1:
                break
            matches.append((pos, keyword))
            idx = pos + 1
    return sorted(matches, key=lambda x: x[0])


def extract_context(text: str, position: int, window: int = CONTEXT_WINDOW) -> str:
    """
    Extract a text window around a keyword position.
    Starts 50 chars before the keyword to include leading context.
    """
    start = max(0, position - 50)
    end = min(len(text), position + window)
    return text[start:end].strip()


def find_ghg_value_in_context(context: str) -> Optional[str]:
    """
    Search for a GHG emission number with unit in a context window.

    Returns:
        The matched string (e.g. "12,450 tCO2e") if found, else None.
        Returns the whole match including unit, not just the number.
    """
    match = GHG_NUMBER_RE.search(context)
    if match:
        # Return the full match text (number + unit)
        return match.group(0).strip()
    return None


def has_absence_phrase(context: str) -> bool:
    """Check if a context window contains a phrase indicating non-disclosure."""
    lower_context = context.lower()
    return any(phrase in lower_context for phrase in ABSENCE_PHRASES)


def classify_state(
    keywords_found: bool,
    value_found: bool,
    absence_detected: bool,
    expects_quantitative: bool,
) -> str:
    """
    Classify the disclosure state of an indicator.

    Rules (applied in priority order):
    1. If absence phrase found and keywords found → not_found
       (explicit non-disclosure is still not_found — absence is the finding)
    2. If no keywords found → not_found
    3. If keywords found and value found (for quantitative indicators) → disclosed
    4. If keywords found and no value (for quantitative indicators) → partially_disclosed
    5. If keywords found (for qualitative indicators) → disclosed

    Returns:
        "disclosed" | "partially_disclosed" | "not_found"
    """
    if not keywords_found:
        return "not_found"

    if absence_detected:
        return "not_found"

    if expects_quantitative and not value_found:
        return "partially_disclosed"

    return "disclosed"


def make_not_found_result(indicator_id: str, brsr_ref: str) -> dict:
    """Standard result dict for an indicator that was not found."""
    return {
        "indicator_id": indicator_id,
        "state": "not_found",
        "value": "",
        "evidence": "",
        "citation": f"Not found in uploaded BRSR filing — {brsr_ref} checked",
        "extraction_method": "keyword",
        "confidence": 0.6,  # Moderate confidence: we checked but keywords are imperfect
        "uncertain": True,
    }


def make_disclosed_result(
    indicator_id: str,
    brsr_ref: str,
    value: str,
    evidence: str,
    confidence: float,
) -> dict:
    """Standard result dict for an indicator that was found."""
    return {
        "indicator_id": indicator_id,
        "state": "disclosed" if value else "partially_disclosed",
        "value": value or "",
        "evidence": evidence[:300],  # Trim long evidence to 300 chars
        "citation": brsr_ref,
        "extraction_method": "keyword",
        "confidence": confidence,
        "uncertain": True,  # Always True for keyword extraction
    }


# ---------------------------------------------------------------------------
# INDICATOR-SPECIFIC EXTRACTION
# ---------------------------------------------------------------------------


def extract_scope3_indicator(text: str, indicator_def: dict) -> dict:
    """
    Scope 3 extraction is handled separately because it requires
    extra metadata fields used by scope3_classifier in analysis_layer.

    Extra fields added to the standard result:
        scope3_mentioned           — bool: any scope 3 keyword found
        scope3_has_absolute_number — bool: absolute tCO2e figure found
        scope3_has_methodology     — bool: named methodology found near scope 3
        scope3_is_intensity_only   — bool: only intensity ratio found, no absolute
        scope3_has_materiality_claim — bool: explicit "not material" statement found

    These flags implement the pre-check layer for the PRD Section 11 decision tree.
    The classifier makes the final verdict; this extractor provides the raw signals.
    """
    indicator_id = indicator_def["indicator_id"]
    brsr_ref = indicator_def["brsr_indicator_ref"]
    keywords = INDICATOR_KEYWORDS.get(indicator_id, [])

    # Base result
    base = {
        "indicator_id": indicator_id,
        "extraction_method": "keyword",
        "uncertain": True,
        "citation": brsr_ref,
        # Scope 3 specific metadata
        "scope3_mentioned": False,
        "scope3_has_absolute_number": False,
        "scope3_has_methodology": False,
        "scope3_is_intensity_only": False,
        "scope3_has_materiality_claim": False,
    }

    lower_text = text.lower()

    # Check for materiality claim first — it is mutually exclusive with other states
    materiality_detected = any(
        phrase in lower_text for phrase in SCOPE3_MATERIALITY_PHRASES
    )
    if materiality_detected:
        return {
            **base,
            "state": "not_found",
            "value": "",
            "evidence": _extract_materiality_evidence(text),
            "confidence": 0.75,
            "scope3_mentioned": True,
            "scope3_has_materiality_claim": True,
        }

    # Find keyword positions
    positions = find_keyword_positions(text, keywords)

    if not positions:
        return {
            **base,
            "state": "not_found",
            "value": "",
            "evidence": "",
            "confidence": 0.65,
        }

    # Scope 3 mentioned — collect evidence from first occurrence
    base["scope3_mentioned"] = True
    first_pos, first_keyword = positions[0]
    context = extract_context(text, first_pos)

    # Check for absolute GHG number
    absolute_value = find_ghg_value_in_context(context)
    if absolute_value:
        base["scope3_has_absolute_number"] = True

    # Check for intensity-only (no absolute, but intensity language present)
    intensity_keywords = [
        "per crore",
        "per tonne of",
        "per unit",
        "intensity",
        "/ crore",
    ]
    has_intensity = any(kw in context.lower() for kw in intensity_keywords)
    if has_intensity and not absolute_value:
        base["scope3_is_intensity_only"] = True

    # Check for methodology near scope 3 context
    methodology_keywords = INDICATOR_KEYWORDS.get("e6_ghg_methodology", [])
    # Look in a wider window for methodology (250 chars)
    wide_context = extract_context(text, first_pos, window=600)
    has_methodology = any(
        kw.lower() in wide_context.lower() for kw in methodology_keywords
    )
    base["scope3_has_methodology"] = has_methodology

    # Classify state
    has_absence = has_absence_phrase(context)
    if has_absence:
        state = "not_found"
        confidence = 0.6
    elif absolute_value:
        state = "disclosed"
        confidence = 0.7
    elif has_intensity:
        state = "partially_disclosed"  # Intensity only = partially in our framework
        confidence = 0.65
    else:
        state = "partially_disclosed"  # Mentioned without quantification
        confidence = 0.60

    return {
        **base,
        "state": state,
        "value": absolute_value or "",
        "evidence": context[:300],
        "confidence": confidence,
    }


def _extract_materiality_evidence(text: str) -> str:
    """Extract the exact sentence containing a Scope 3 materiality claim."""
    lower_text = text.lower()
    for phrase in SCOPE3_MATERIALITY_PHRASES:
        idx = lower_text.find(phrase)
        if idx != -1:
            return extract_context(text, idx, window=200)
    return ""


def extract_generic_indicator(text: str, indicator_def: dict) -> dict:
    """
    Standard extraction for non-Scope-3 indicators.
    Works for both quantitative and qualitative indicators.
    """
    indicator_id = indicator_def["indicator_id"]
    brsr_ref = indicator_def["brsr_indicator_ref"]
    expects_quantitative = indicator_def.get("expected_data") == "quantitative"
    keywords = INDICATOR_KEYWORDS.get(indicator_id, [])

    if not keywords:
        # No keywords defined for this indicator — return not_found with low confidence
        return {
            **make_not_found_result(indicator_id, brsr_ref),
            "confidence": 0.3,
        }

    positions = find_keyword_positions(text, keywords)

    #debugging print
    print(
    f"[extract] {indicator_id} | matches={len(positions)}"
)

    if not positions:
        return make_not_found_result(indicator_id, brsr_ref)
    # Use the first occurrence for context extraction
    first_pos, first_keyword = positions[0]
    context = extract_context(text, first_pos)

    
   #context print immediately shows what text the extractor is seeing
    print(
    f"[context] {indicator_id}\n"
    f"keyword='{first_keyword}'\n"
    f"{context[:250]}\n"
    f"{'-'*60}"
)

    # Check for absence phrases in the context
    absence_detected = has_absence_phrase(context)

    # Try to find a GHG value if this is a quantitative indicator
    value = None
    if expects_quantitative:
        value = find_ghg_value_in_context(context)

    # For energy/water/waste, also try a simpler number search
    # since units vary more than GHG units
    if expects_quantitative and not value:
        value = _find_generic_number(context)

    state = classify_state(
        keywords_found=True,
        value_found=bool(value),
        absence_detected=absence_detected,
        expects_quantitative=expects_quantitative,
    )

    if state == "not_found":
        return make_not_found_result(indicator_id, brsr_ref)

    confidence = 0.70 if value else 0.55


    print(
    f"[extract] {indicator_id} | "
    f"matches={len(positions)} | "
    f"value={value} | "
    f"state={state}"
)
    return make_disclosed_result(
        indicator_id=indicator_id,
        brsr_ref=brsr_ref,
        value=value or "",
        evidence=context,
        confidence=confidence,
    )

    

def _find_generic_number(context: str) -> Optional[str]:
    """
    Fallback number finder for non-GHG quantitative indicators.
    Supports both:

    3685 KL
    Groundwater (KL) 3685
    """

    patterns = [
        # Number followed by unit
        re.compile(
            r"([\d,]+(?:\.\d+)?)"
            r"\s*"
            r"(?:kl|kilolitre|kiloliter|ml|litre|liter|mt|kg|tonne|kwh|gj|tj|mwh)",
            re.IGNORECASE,
        ),
        re.compile(
            r"\((?:kl|kg|mt|gj|tj|kwh|kg/kl)\)\s*([\d,]+(?:\.\d+)?)", re.IGNORECASE
        ),
        # Unit followed by number
        re.compile(
            r"(?:kl|kilolitre|kiloliter|ml|litre|liter|mt|kg|tonne|kwh|gj|tj|mwh)"
            r"[^0-9]{0,20}"
            r"([\d,]+(?:\.\d+)?)",
            re.IGNORECASE,
        ),
    ]

    for pattern in patterns:
        match = pattern.search(context)
        if match:
            print(f"[generic_number] matched: {match.group(0)}")
            return match.group(0).strip()
        if match:
            return match.group(0).strip()

    return None


# ---------------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------------


def extract_principle_indicators(
    principle_indicators: dict,
    brsr_section_text: str,
) -> dict:
    """
    Run keyword extraction for all indicators in a principle.

    Args:
        principle_indicators: The "indicators" dict from the schema for one principle.
        brsr_section_text:    The extracted BRSR section text from quality_check.

    Returns:
        Dict mapping indicator_id → extraction result dict.
        Every indicator in the schema appears in the output,
        even if its state is "not_found".

    Design note:
        Every indicator gets a result, regardless of whether it was found.
        This guarantees that downstream nodes (analysis_layer, compile_brief)
        never encounter a KeyError when looking up an indicator.
    """
    results = {}

    # Scope 3 receives dedicated handling because it drives supplier-risk
    # assessment in downstream analysis. Unlike other indicators, we must
    # distinguish between:
    #   - quantified Scope 3 disclosure,
    #   - intensity-only disclosure,
    #   - methodology disclosure,
    #   - explicit materiality/non-applicability claims.
    # These signals are later consumed by scope3_classifier and procurement
    # risk logic, so a specialized extraction path is required.

    for indicator_id, indicator_def in principle_indicators.items():
        if indicator_id == "e6_scope3_emissions":
            result = extract_scope3_indicator(brsr_section_text, indicator_def)
        else:
            result = extract_generic_indicator(brsr_section_text, indicator_def)

        # Sanity check: ensure required keys are always present to protect against bugs in individual extractors
        # This ensure
        # - Only repair missing fields.
        # - Never overwrite existing fields.
        result.setdefault("indicator_id", indicator_id)
        result.setdefault("extraction_method", "keyword")
        result.setdefault("uncertain", True)

        results[indicator_id] = result

    return results

