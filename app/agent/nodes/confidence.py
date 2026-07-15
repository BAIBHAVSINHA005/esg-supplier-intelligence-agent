# app/agent/nodes/confidence.py
#
# Node 5: Assess extraction quality and produce a confidence verdict.
#
# Reads:   extraction_confidence_score  (quality_check)
#          is_machine_readable          (quality_check)
#          brsr_section_found           (quality_check)
#          extracted_indicators         (extract_indicators)
#          completeness_results         (analysis_layer)
#          document_failure             (ingest_document / quality_check)
#
# Writes:  confidence_level
#          confidence_directive
#          hitl_flag
#          uncertain_fields
#
# Pure deterministic Python. No LLM calls. No schema loading.
# All signal extraction is from state fields already computed upstream.
#
# ─────────────────────────────────────────────────────────────────────────────
# CONFIDENCE LEVEL DEFINITIONS (PRD Section 14)
#
# HIGH    All three conditions true:
#           • extraction_method is not stub
#           • doc_score >= 0.75
#           • extraction_ratio >= 0.80
#           • uncertain_fields is empty
#
# MEDIUM  Neither High nor Low. Covers:
#           • Stub extraction with good document quality
#           • Keyword extraction (always uncertain=True on found fields)
#           • doc_score >= 0.50 but extraction_ratio < 0.80
#
# LOW     Any structural failure:
#           • Document not machine-readable
#           • BRSR section not found
#           • extraction_ratio < 0.50 on real (non-stub) extraction
#
# Note:   If document_failure is True, execution is on the handle_failure path
#         and this node does not run. The early-return guard below handles the
#         edge case where state is malformed and document_failure was not set.
# ─────────────────────────────────────────────────────────────────────────────

from app.agent.state import AssessmentState


# ── PRD Section 14 directive strings ─────────────────────────────────────────
# Exact text as specified in the PRD. Do not paraphrase.

_DIRECTIVES: dict[str, str] = {
    "high": (
        "Extraction quality is high. This brief can be used as the basis for "
        "procurement decision-making. Verify any specific claim by "
        "cross-referencing the cited section in the source document before "
        "acting on it."
    ),
    "medium": (
        "Some sections had extraction uncertainty. Fields marked [\u26a0] in "
        "this brief should be manually verified against the source document "
        "before acting on them. The Scope 3 readiness verdict and Completeness "
        "Assessment are reliable for principles where extraction was clean."
    ),
    "low": (
        "Significant extraction limitations were detected in the uploaded "
        "document. This brief must not be used for procurement decisions "
        "without full human review of the source BRSR filing. The findings "
        "below are indicative only."
    ),
}

# Thresholds — isolated here so they can be adjusted without reading the logic.
_DOC_SCORE_HIGH_THRESHOLD   = 0.75   # extraction_confidence_score >= this → not low from doc quality
_DOC_SCORE_LOW_THRESHOLD    = 0.50   # extraction_confidence_score < this → low
_EXTR_RATIO_HIGH_THRESHOLD  = 0.80   # extraction_ratio >= this → candidate for high
_EXTR_RATIO_LOW_THRESHOLD   = 0.50   # extraction_ratio < this → low (non-stub only)
_UNCERTAIN_COUNT_HITL_LIMIT = 2      # uncertain_fields > this → HITL flag on medium


# ── Signal extraction helpers ─────────────────────────────────────────────────

def _detect_extraction_method(extracted: dict) -> str:
    """
    Determine the primary extraction method across all extracted indicators.

    Returns the most informative method name found:
        "llm"     — at least one LLM extraction present
        "keyword" — at least one keyword extraction, no LLM
        "stub"    — only stub extractions or no extractions at all

    Used to decide whether extraction_ratio is meaningful and whether
    High confidence is achievable.
    """
    methods: set[str] = set()
    for principle_indicators in extracted.values():
        for ind_data in principle_indicators.values():
            methods.add(ind_data.get("extraction_method", "stub"))

    if "llm" in methods:
        return "llm"
    if "keyword" in methods:
        return "keyword"
    return "stub"


def _compute_extraction_ratio(completeness_results: list[dict]) -> float | None:
    """
    Compute the ratio of essential indicators that were found (disclosed or
    partially_disclosed) across all assessed principles.

    Uses completeness_results rather than re-iterating extracted_indicators
    directly, because analysis_layer already applied schema-aware essential vs
    leadership classification. This avoids duplicating that logic here.

    Returns:
        float in [0.0, 1.0] if completeness_results contains usable data
        None if completeness_results is empty (cannot compute)
    """
    total_essential = sum(r.get("essential_total", 0) for r in completeness_results)
    total_disclosed = sum(
        r.get("essential_disclosed", 0) + r.get("essential_partial", 0)
        for r in completeness_results
    )

    if total_essential == 0:
        return None

    return total_disclosed / total_essential


def _find_uncertain_fields(extracted: dict) -> list[str]:
    """
    Identify indicator fields where extraction produced a finding but
    the finding is marked as uncertain.

    Only includes indicators with state in (disclosed, partially_disclosed).
    Not-found indicators are omitted — absence is a stated finding, not
    an uncertain one.

    Field ID format: "principle_6.e6_scope3_emissions"
    This format matches the structure of extracted_indicators and gives
    compile_brief enough information to locate and mark each field.

    Phase 3 (stub extraction):
        uncertain_fields will be empty — stub indicators are all not_found,
        so no found-but-uncertain states exist.

    Phase 3 (keyword extraction):
        uncertain_fields includes all disclosed/partially_disclosed indicators
        because keyword extraction always sets uncertain=True.

    Phase 4 (LLM extraction):
        uncertain_fields includes only indicators where the LLM extraction
        set uncertain=True. High-confidence LLM results set uncertain=False
        and are excluded.
    """
    uncertain: list[str] = []

    for principle_id, principle_indicators in extracted.items():
        for ind_id, ind_data in principle_indicators.items():
            is_found_state = ind_data.get("state") in (
                "disclosed",
                "partially_disclosed",
            )
            is_uncertain = ind_data.get("uncertain", True)

            if is_found_state and is_uncertain:
                uncertain.append(f"{principle_id}.{ind_id}")

    return sorted(uncertain)


# ── Level determination ───────────────────────────────────────────────────────

def _determine_level(
    is_machine_readable:  bool,
    brsr_section_found:   bool,
    doc_score:            float,
    extraction_method:    str,
    extraction_ratio:     float | None,
    uncertain_fields:     list[str],
) -> tuple[str, str]:
    """
    Assign a confidence level and produce a plain-English rationale string.

    Returns:
        (level, rationale) where level is "high" | "medium" | "low"
        and rationale explains the decision in one sentence.
        rationale is for logging and debugging — it does not appear in the brief.

    Decision tree (applied top-down, first match wins):

    1. LOW — structural document failures
       • Not machine-readable (scanned/image PDF)
       • BRSR section not found

    2. LOW — real extraction with poor coverage
       • extraction_method is not stub
       • AND extraction_ratio < 0.50

    3. HIGH — all quality signals strong
       • extraction_method is not stub (stub cannot be High — PRD Section 14)
       • AND doc_score >= _DOC_SCORE_HIGH_THRESHOLD
       • AND extraction_ratio >= _EXTR_RATIO_HIGH_THRESHOLD
       • AND uncertain_fields is empty (no found-but-uncertain indicators)

    4. MEDIUM — default (everything not caught above)
       • Includes stub with good document quality
       • Includes keyword extraction (always uncertain)
       • Includes doc_score between thresholds
    """
    is_stub = extraction_method == "stub"

    # ── Check 1: Structural document failures → LOW ───────────────────────────
    if not is_machine_readable:
        return (
            "low",
            "Document is not machine-readable. Text extraction produced "
            f"{doc_score:.2f} document quality score.",
        )

    if not brsr_section_found:
        return (
            "low",
            "BRSR section could not be identified in the uploaded document. "
            f"Document quality score: {doc_score:.2f}.",
        )

    # ── Check 2: Real extraction with poor indicator coverage → LOW ───────────
    if not is_stub and extraction_ratio is not None:
        if extraction_ratio < _EXTR_RATIO_LOW_THRESHOLD:
            return (
                "low",
                f"Only {extraction_ratio:.0%} of essential indicators were located. "
                f"Minimum for reliable assessment is {_EXTR_RATIO_LOW_THRESHOLD:.0%}. "
                f"Document quality: {doc_score:.2f}.",
            )

    # ── Check 3: All quality signals strong → HIGH ────────────────────────────
    # Stub extraction is explicitly excluded — a stub cannot claim High confidence
    # regardless of document quality because no real extraction has occurred.
    if (
        not is_stub
        and doc_score >= _DOC_SCORE_HIGH_THRESHOLD
        and extraction_ratio is not None
        and extraction_ratio >= _EXTR_RATIO_HIGH_THRESHOLD
        and len(uncertain_fields) == 0
    ):
        return (
            "high",
            f"Document quality {doc_score:.2f}, extraction ratio "
            f"{extraction_ratio:.0%}, no uncertain findings.",
        )

    # ── Check 4: Default → MEDIUM ─────────────────────────────────────────────
    if is_stub:
        rationale = (
            f"Stub extraction — real extraction not yet performed. "
            f"Document quality score: {doc_score:.2f}."
        )
    elif extraction_ratio is not None:
        rationale = (
            f"Document quality {doc_score:.2f}, extraction ratio "
            f"{extraction_ratio:.0%}, {len(uncertain_fields)} uncertain "
            f"field(s) require verification."
        )
    else:
        rationale = (
            f"Document quality {doc_score:.2f}. "
            f"Extraction ratio not available."
        )

    return "medium", rationale


def _determine_hitl_flag(
    level:            str,
    is_stub:          bool,
    uncertain_fields: list[str],
) -> bool:
    """
    Set the HITL flag based on confidence level and extraction state.

    Rules:
        Low:    always True — brief should not be acted on without review
        Stub:   always True — stub extraction is not a real assessment
        Medium: True if uncertain_fields count exceeds the HITL limit
        High:   False — brief is reliable enough to use directly

    Note: is_stub is a separate parameter rather than inferred from level
    because a stub extraction produces Medium, not Low — but it still
    requires HITL for the same underlying reason as Low.
    """
    if level == "low":
        return True
    if is_stub:
        return True
    if level == "medium" and len(uncertain_fields) > _UNCERTAIN_COUNT_HITL_LIMIT:
        return True
    return False


# ── Node entry point ──────────────────────────────────────────────────────────

def assess_confidence(state: AssessmentState) -> dict:
    """
    Node 5: Compute confidence level, directive, HITL flag, and uncertain fields.

    Reads:  extraction_confidence_score, is_machine_readable, brsr_section_found,
            extracted_indicators, completeness_results, document_failure
    Writes: confidence_level, confidence_directive, hitl_flag, uncertain_fields
    """
    print("[assess_confidence]")

    # ── Upstream failure guard ────────────────────────────────────────────────
    # If document_failure is True, execution should have routed to handle_failure.
    # This guard handles the edge case where that routing did not occur.
    if state.get("document_failure", False):
        print("[assess_confidence] Upstream document failure — returning low confidence")
        return {
            "confidence_level":     "low",
            "confidence_directive": _DIRECTIVES["low"],
            "hitl_flag":            True,
            "uncertain_fields":     [],
        }

    # ── Read signals from state ───────────────────────────────────────────────
    doc_score            = state.get("extraction_confidence_score", 0.0)
    is_machine_readable  = state.get("is_machine_readable", True)
    brsr_section_found   = state.get("brsr_section_found", True)
    extracted            = state.get("extracted_indicators", {})
    completeness_results = state.get("completeness_results", [])

    # ── Compute derived signals ───────────────────────────────────────────────
    extraction_method = _detect_extraction_method(extracted)
    extraction_ratio  = _compute_extraction_ratio(completeness_results)
    uncertain_fields  = _find_uncertain_fields(extracted)
    is_stub           = extraction_method == "stub"

    # ── Determine level ───────────────────────────────────────────────────────
    level, rationale = _determine_level(
        is_machine_readable = is_machine_readable,
        brsr_section_found  = brsr_section_found,
        doc_score           = doc_score,
        extraction_method   = extraction_method,
        extraction_ratio    = extraction_ratio,
        uncertain_fields    = uncertain_fields,
    )

    # ── Determine HITL flag ───────────────────────────────────────────────────
    hitl_flag = _determine_hitl_flag(
        level            = level,
        is_stub          = is_stub,
        uncertain_fields = uncertain_fields,
    )

    # ── Logging ───────────────────────────────────────────────────────────────
    ratio_display = f"{extraction_ratio:.0%}" if extraction_ratio is not None else "n/a"

    print(f"[assess_confidence] doc_score={doc_score:.2f}  "
          f"method={extraction_method}  "
          f"ratio={ratio_display}  "
          f"uncertain={len(uncertain_fields)}")
    print(f"[assess_confidence] Level: {level.upper()}  |  HITL: {hitl_flag}")
    print(f"[assess_confidence] Rationale: {rationale}")

    if uncertain_fields:
        print(f"[assess_confidence] Uncertain fields ({len(uncertain_fields)}):")
        for field in uncertain_fields:
            print(f"  ⚠  {field}")

    # ── Return ────────────────────────────────────────────────────────────────
    return {
        "confidence_level":     level,
        "confidence_directive": _DIRECTIVES[level],
        "hitl_flag":            hitl_flag,
        "uncertain_fields":     uncertain_fields,
    }