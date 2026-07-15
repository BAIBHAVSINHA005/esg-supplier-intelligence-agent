# app/agent/nodes/analysis.py
#
# Node 4: Classify Scope 3 readiness, assess Principle 6 completeness,
# and detect procurement-relevant disclosure gaps.
#
# Reads:  extracted_indicators, document_failure
# Writes: scope3_verdict, completeness_results, gaps
#
# Pure deterministic Python — no LLM calls, no ChromaDB, no API costs.
# All logic is a direct implementation of PRD Sections 11, 12, and 13.
#
# Structure:
#   SECTION 1 — Scope 3 classification (_classify_scope3)
#   SECTION 2 — Maturity signal extraction (_extract_maturity_signals)
#   SECTION 3 — Completeness assessment (_assess_p6_completeness)
#   SECTION 4 — Gap detection (_detect_gaps)
#   SECTION 5 — Node entry point (analysis_layer)

from app.agent.state import AssessmentState
from app.schemas.loader import load_schema


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — SCOPE 3 CLASSIFICATION
# Implements the PRD Section 11 decision tree exactly.
# ═══════════════════════════════════════════════════════════════════════════════

# Base dicts for each level — merged with evidence and citation at classification time.
# Using constants prevents typos in level strings across the codebase.
_SCOPE3_LEVELS = {
    "not_found": {
        "level":        "not_found",
        "level_number": 0,
        "label":        "Not Found in Uploaded BRSR Filing",
    },
    "materiality_claim": {
        "level":        "materiality_claim",
        "level_number": None,
        "label":        "Materiality Claim — Supplier states Scope 3 is not applicable",
    },
    "claim_only": {
        "level":        "claim_only",
        "level_number": 1,
        "label":        "Claim Only — Acknowledged without a usable absolute figure",
    },
    "partial": {
        "level":        "partial",
        "level_number": 2,
        "label":        "Partial — Either absolute figure or methodology present, not both",
    },
    "scope3_ready": {
        "level":        "scope3_ready",
        "level_number": 3,
        "label":        "Scope 3 Ready — Absolute figure and named methodology both present",
    },
}


def _classify_scope3(scope3_indicator: dict) -> dict:
    """
    Apply the PRD Section 11 decision tree to the Scope 3 indicator result.

    Decision tree (applied in strict priority order):

    1. Not mentioned at all               → not_found
    2. Explicit materiality claim         → materiality_claim
    3. Absolute figure AND methodology    → scope3_ready
    4. Absolute figure OR methodology     → partial
    5. Intensity ratio only               → claim_only   (PRD Decision 2, Option B)
    6. Mentioned without quantification   → claim_only

    Arguments:
        scope3_indicator — the extraction result dict for e6_scope3_emissions.
                           All reads use .get() so this function works correctly
                           with both the stub extractor (no scope3-specific fields)
                           and the keyword extractor (scope3-specific fields present).

    Returns:
        A scope3 verdict dict. Fields always present:
            level, level_number, label, evidence, citation
        Fields conditionally present:
            partial_detail  — on "partial": what is present and what is missing
            claim_detail    — on "claim_only": reason for the claim-only classification
        Field always added by the caller (not this function):
            maturity_signals
    """
    mentioned         = scope3_indicator.get("scope3_mentioned", False)
    has_absolute      = scope3_indicator.get("scope3_has_absolute_number", False)
    has_methodology   = scope3_indicator.get("scope3_has_methodology", False)
    is_intensity_only = scope3_indicator.get("scope3_is_intensity_only", False)
    materiality_claim = scope3_indicator.get("scope3_has_materiality_claim", False)

    state    = scope3_indicator.get("state", "not_found")
    evidence = scope3_indicator.get("evidence", "")
    citation = scope3_indicator.get(
        "citation",
        "Principle 6, Leadership Indicator"
    )

    # Fallback: if the extractor did not set scope3_mentioned (e.g. stub extractor),
    # infer from the extraction state so the decision tree still runs correctly.
    if not mentioned and not materiality_claim:
        if state in ("disclosed", "partially_disclosed"):
            mentioned = True

    # ── Step 1: Not mentioned ────────────────────────────────────────────────
    if not mentioned and not materiality_claim:
        return {
            **_SCOPE3_LEVELS["not_found"],
            "evidence": evidence or "No Scope 3 content located in the uploaded filing.",
            "citation": f"Not found in uploaded BRSR filing — {citation} checked",
        }

    # ── Step 2: Materiality claim ────────────────────────────────────────────
    if materiality_claim:
        return {
            **_SCOPE3_LEVELS["materiality_claim"],
            "evidence": evidence,
            "citation": citation,
        }

    # ── Step 3: Both required elements present ───────────────────────────────
    if has_absolute and has_methodology:
        return {
            **_SCOPE3_LEVELS["scope3_ready"],
            "evidence": evidence,
            "citation": citation,
        }

    # ── Step 4: Exactly one of the two required elements present ────────────
    if has_absolute or has_methodology:
        present = "absolute figure in tCO2e" if has_absolute else "named methodology"
        missing = "named methodology"         if has_absolute else "absolute figure in tCO2e"
        return {
            **_SCOPE3_LEVELS["partial"],
            "evidence":       evidence,
            "citation":       citation,
            "partial_detail": {
                "present": present,
                "missing": missing,
            },
        }

    # ── Step 5: Intensity ratio only — PRD Decision 2, Option B ─────────────
    # Intensity ratios (tCO2e per crore, per tonne of output) are not usable
    # for supply chain Scope 3 accounting and are classified as Claim Only,
    # not Partial. This is the explicit decision locked in the PRD.
    if is_intensity_only:
        return {
            **_SCOPE3_LEVELS["claim_only"],
            "evidence":     evidence,
            "citation":     citation,
            "claim_detail": (
                "Intensity ratio disclosed without an absolute tCO2e figure. "
                "Intensity ratios cannot be aggregated into a buyer's Scope 3 "
                "inventory and do not satisfy Scope 3 Ready classification."
            ),
        }

    # ── Step 6: Mentioned but not quantified ─────────────────────────────────
    return {
        **_SCOPE3_LEVELS["claim_only"],
        "evidence":     evidence,
        "citation":     citation,
        "claim_detail": "Scope 3 acknowledged qualitatively without quantification.",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — MATURITY SIGNAL EXTRACTION
# Supplementary signals that accompany the verdict but do not change its level.
# ═══════════════════════════════════════════════════════════════════════════════

def _extract_maturity_signals(scope3_indicator: dict, p6_indicators: dict) -> dict:
    """
    Extract Scope 3 maturity signals from available extracted data.

    These signals are displayed in the brief alongside the verdict
    but do not affect the level classification.

    Signal values:
        "found"        — detected in the extracted data
        "not_found"    — actively checked and not found
        "not_assessed" — cannot be determined from keyword extraction alone;
                         Phase 4 LLM extraction will resolve these

    Signals assessable in Phase 3 (keyword extraction):
        sbti               — inferred from e6_climate_target evidence
        category_boundary  — inferred from scope3 evidence text

    Signals deferred to Phase 4:
        assurance          — requires reading the assurance statement section
        significant_partners — requires reading value-chain section (other principles)
        trend_data         — requires comparing multi-year data
    """
    signals = {
        "assurance":            "not_assessed",
        "category_boundary":    "not_assessed",
        "sbti":                 "not_found",
        "significant_partners": "not_assessed",
        "trend_data":           "not_assessed",
    }

    # SBTi: check evidence from the climate target indicator
    climate  = p6_indicators.get("e6_climate_target", {})
    combined = (
        climate.get("evidence", "") + " " + climate.get("value", "")
    ).lower()
    sbti_keywords = [
        "sbti",
        "science based target",
        "science-based target",
        "1.5 degree",
        "1.5°c",
    ]
    if any(kw in combined for kw in sbti_keywords):
        signals["sbti"] = "found"

    # Category boundary: check whether scope3 evidence names specific categories
    scope3_evidence = scope3_indicator.get("evidence", "").lower()
    boundary_signals = [
        "category 1", "category 3", "category 11", "category 12",
        "scope 3 categories", "following categories", "categories include",
        "cat 1", "cat 3",
    ]
    if any(kw in scope3_evidence for kw in boundary_signals):
        signals["category_boundary"] = "found"

    return signals


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — COMPLETENESS ASSESSMENT
# Implements PRD Section 12 per-principle completeness rules.
# ═══════════════════════════════════════════════════════════════════════════════

def _assess_p6_completeness(p6_indicators: dict, schema_indicators: dict) -> dict:
    """
    Assess disclosure completeness for Principle 6 (Environment).

    Completeness state rules (PRD Section 12):
        Complete  — all essential indicators are "disclosed"
        Partial   — at least one essential "disclosed" AND at least one
                    "partially_disclosed" or "not_found"
        Not Found — all essential indicators are "not_found"

    Leadership indicators (e6_scope3_emissions) are tallied separately and
    do not affect the essential completeness state. Their status is tracked
    in "leadership_disclosed" for use by compile_brief.

    Arguments:
        p6_indicators     — the principle_6 extraction results dict
        schema_indicators — the schema "indicators" dict for principle_6,
                            used to determine which indicators are essential
                            vs leadership without hardcoding IDs here

    Returns:
        A single completeness result dict for Principle 6.
    """
    essential_ids  = [
        ind_id for ind_id, defn in schema_indicators.items()
        if defn.get("type") == "essential"
    ]
    leadership_ids = [
        ind_id for ind_id, defn in schema_indicators.items()
        if defn.get("type") == "leadership"
    ]

    # Tally essential indicators by state
    essential_disclosed = []
    essential_partial   = []
    essential_not_found = []

    for ind_id in essential_ids:
        ind_state = p6_indicators.get(ind_id, {}).get("state", "not_found")
        if ind_state == "disclosed":
            essential_disclosed.append(ind_id)
        elif ind_state == "partially_disclosed":
            essential_partial.append(ind_id)
        else:
            essential_not_found.append(ind_id)

    # Tally leadership indicators
    leadership_disclosed = [
        ind_id for ind_id in leadership_ids
        if p6_indicators.get(ind_id, {}).get("state") == "disclosed"
    ]

    total    = len(essential_ids)
    n_disc   = len(essential_disclosed)
    n_part   = len(essential_partial)
    n_absent = len(essential_not_found)

    # Assign completeness state
    if total == 0 or n_absent == total:
        comp_state = "not_found"
    elif n_disc == total:
        comp_state = "complete"
    else:
        comp_state = "partial"

    # Citation string
    if comp_state == "not_found":
        citation = (
            "Not found in uploaded BRSR filing — "
            "Principle 6 essential indicators checked"
        )
    elif comp_state == "complete":
        citation = "Principle 6, Section C — all essential indicators disclosed"
    else:
        citation = (
            f"Principle 6, Section C — "
            f"{n_disc} of {total} essential indicators disclosed"
        )

    return {
        "principle_number":     6,
        "principle_name":       "Environment",
        "state":                comp_state,
        "citation":             citation,
        "essential_total":      total,
        "essential_disclosed":  n_disc,
        "essential_partial":    n_part,
        "essential_not_found":  n_absent,
        "partial_indicators":   essential_partial,
        "not_found_indicators": essential_not_found,
        "leadership_disclosed": leadership_disclosed,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — GAP DETECTION
# Implements PRD Section 13 gap priority framework.
# ═══════════════════════════════════════════════════════════════════════════════

# Internal priority values used for sorting before rank assignment.
# Lower number = higher priority. Not exposed in the output.
_PRIORITY = {
    "G-01": 10,
    "G-02": 20,
    "G-03": 30,
    "G-05": 40,
    "G-10": 50,
    "G-11": 60,
}


def _detect_gaps(
    p6_indicators:  dict,
    scope3_verdict: dict,
    completeness:   dict,
) -> list[dict]:
    """
    Identify the top 5 most procurement-relevant disclosure gaps from Principle 6.

    Gap definitions, trigger conditions, and priority order come directly from
    PRD Section 13. Only gaps that can be deterministically assessed from
    Principle 6 data are included here.

    Gaps requiring other principles (G-06 human rights, G-07 value-chain,
    G-08 assurance, G-09 significant partners) are deferred until those
    principles are extracted.

    Gap trigger map (Principle 6 subset):
        G-01 Critical  — Scope 3 Level 0, 1, or Materiality Claim
        G-02 Critical  — GHG methodology not named
        G-03 Critical  — Principle 6 severely incomplete (fewer than 2 of 8 essential)
        G-05 Critical  — No climate or emissions reduction target
        G-10 Notable   — Intensity metrics absent when absolutes are present
        G-11 Minor     — Leadership indicators not addressed
                         (suppressed if G-01 is triggered — same underlying gap)

    Returns:
        List of up to 5 gap dicts, sorted by priority then ranked 1–5.
        Each dict contains: rank, gap_id, gap_name, brsr_reference,
        severity, description, citation.
    """
    triggered = []

    def _add(gap_id, gap_name, brsr_ref, severity, description, citation):
        triggered.append({
            "gap_id":         gap_id,
            "gap_name":       gap_name,
            "brsr_reference": brsr_ref,
            "severity":       severity,
            "description":    description,
            "citation":       citation,
            "_priority":      _PRIORITY.get(gap_id, 99),
        })

    # ── G-01: Scope 3 not disclosed ──────────────────────────────────────────
    scope3_level = scope3_verdict.get("level", "not_found")
    if scope3_level in ("not_found", "claim_only", "materiality_claim"):
        if scope3_level == "materiality_claim":
            desc = (
                "Supplier has formally stated that Scope 3 emissions are not material "
                "to its operations. No quantified Scope 3 data is provided. The basis "
                "for this materiality determination has not been independently verified "
                "from this filing. Request the supplier's materiality assessment "
                "documentation."
            )
        elif scope3_level == "claim_only":
            desc = (
                "Supplier acknowledges Scope 3 emissions but does not provide a "
                "quantified absolute figure usable for supply chain carbon accounting. "
                "Intensity ratios and qualitative references do not satisfy Scope 3 "
                "Ready classification."
            )
        else:
            desc = (
                "No Scope 3 emissions data was found in the uploaded BRSR filing. "
                "Scope 3 data is required for the buyer's own value-chain disclosure "
                "obligations and supply chain carbon inventory."
            )
        _add(
            "G-01",
            "Scope 3 not disclosed",
            "Principle 6, Leadership Indicator",
            "critical",
            desc,
            scope3_verdict.get("citation", "Principle 6 checked"),
        )

    # ── G-02: No GHG accounting methodology ─────────────────────────────────
    methodology = p6_indicators.get("e6_ghg_methodology", {})
    if methodology.get("state", "not_found") == "not_found":
        _add(
            "G-02",
            "No GHG accounting methodology named",
            "Principle 6, Essential Indicator E-4",
            "critical",
            (
                "No GHG accounting methodology is named in the filing "
                "(e.g. GHG Protocol Corporate Standard, ISO 14064-1). "
                "A named methodology is required for Scope 3 Ready classification "
                "and is a prerequisite for audit-grade emissions disclosure."
            ),
            methodology.get(
                "citation",
                "Not found in uploaded BRSR filing — "
                "Principle 6, Essential Indicator E-4 checked",
            ),
        )

    # ── G-03: Principle 6 severely incomplete ────────────────────────────────
    # Threshold: fewer than 2 of 8 essential indicators disclosed.
    # This gap signals a systemic disclosure failure, not an individual gap —
    # hence it only triggers when the situation is severe.
    n_disc  = completeness.get("essential_disclosed", 0)
    n_total = completeness.get("essential_total", 1)
    if n_disc < 2 and n_total >= 4:
        _add(
            "G-03",
            "Principle 6 environmental data severely incomplete",
            "Principle 6, Section C Essential Indicators",
            "critical",
            (
                f"Only {n_disc} of {n_total} essential environmental indicators "
                f"were found in this filing. Core GHG performance data is insufficient "
                f"for a procurement ESG assessment."
            ),
            completeness.get("citation", "Principle 6, Section C checked"),
        )

    # ── G-05: No climate target ──────────────────────────────────────────────
    climate = p6_indicators.get("e6_climate_target", {})
    if climate.get("state", "not_found") == "not_found":
        _add(
            "G-05",
            "No climate or emissions reduction target disclosed",
            "Principle 6, Essential Indicator E-6",
            "critical",
            (
                "No emissions reduction target was found in the filing. "
                "Absence of a climate target is a material signal for buyers "
                "with Net Zero or SBTi commitments who require supply chain "
                "climate alignment."
            ),
            climate.get(
                "citation",
                "Not found in uploaded BRSR filing — "
                "Principle 6, Essential Indicator E-6 checked",
            ),
        )

    # ── G-10: Intensity metrics absent when absolutes are present ───────────
    # Only meaningful if absolute Scope 1 or 2 figures exist.
    # If absolutes are absent, G-03 already covers the severity of that gap.
    scope1    = p6_indicators.get("e6_scope1_emissions", {})
    scope2    = p6_indicators.get("e6_scope2_emissions", {})
    intensity = p6_indicators.get("e6_ghg_intensity", {})
    absolutes_present = (
        scope1.get("state") in ("disclosed", "partially_disclosed") or
        scope2.get("state") in ("disclosed", "partially_disclosed")
    )
    if absolutes_present and intensity.get("state", "not_found") == "not_found":
        _add(
            "G-10",
            "GHG emission intensity metrics absent",
            "Principle 6, Essential Indicator E-5",
            "notable",
            (
                "Absolute GHG figures are disclosed but emission intensity metrics "
                "(emissions per unit of revenue or production) are absent. "
                "Intensity metrics enable year-on-year performance comparison "
                "independent of production volume changes."
            ),
            intensity.get(
                "citation",
                "Not found in uploaded BRSR filing — "
                "Principle 6, Essential Indicator E-5 checked",
            ),
        )

    # ── G-11: Leadership indicators not addressed ────────────────────────────
    # Suppressed when G-01 is triggered — they describe the same underlying gap.
    # Only surfaces when Scope 3 is state="not_found" from the extractor but
    # G-01 did not trigger (e.g. the stub extractor returned not_found without
    # setting scope3_mentioned=False explicitly).
    g01_present = any(g["gap_id"] == "G-01" for g in triggered)
    scope3_ind  = p6_indicators.get("e6_scope3_emissions", {})
    if not g01_present and scope3_ind.get("state", "not_found") == "not_found":
        _add(
            "G-11",
            "Leadership indicators not addressed",
            "Principle 6, Leadership Indicator — Scope 3",
            "minor",
            (
                "The Scope 3 leadership indicator was not addressed in this filing. "
                "While voluntary, leadership indicators signal ESG maturity and are "
                "increasingly expected by buyers with supply chain decarbonisation "
                "commitments."
            ),
            scope3_ind.get(
                "citation",
                "Not found in uploaded BRSR filing — "
                "Principle 6 Leadership Indicator checked",
            ),
        )

    # ── Select top 5, assign ranks ───────────────────────────────────────────
    triggered.sort(key=lambda g: g["_priority"])
    top_5 = triggered[:5]

    return [
        {k: v for k, v in {**gap, "rank": rank}.items() if k != "_priority"}
        for rank, gap in enumerate(top_5, start=1)
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — NODE ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def analysis_layer(state: AssessmentState) -> dict:
    """
    Node 4: Classify Scope 3 readiness, assess completeness, detect gaps.

    Reads:  extracted_indicators, document_failure
    Writes: scope3_verdict, completeness_results, gaps

    This node does not read the source document. It operates entirely
    on the structured output produced by extract_indicators.
    All raw document access ends when quality_check finishes.
    """
    print("[analysis_layer]")

    if state.get("document_failure", False):
        print("[analysis_layer] Upstream failure — skipping")
        return {
            "scope3_verdict":       _empty_scope3_verdict(),
            "completeness_results": [],
            "gaps":                 [],
        }

    extracted = state.get("extracted_indicators", {})
    p6 = extracted.get("principle_6", {})

    if not p6:
        print("[analysis_layer] WARNING: extracted_indicators is empty — "
              "returning empty verdict")
        return {
            "scope3_verdict":       _empty_scope3_verdict(),
            "completeness_results": [],
            "gaps":                 [],
        }

    # Load schema for indicator type metadata (essential vs leadership)
    schema            = load_schema("brsr_v2023")
    schema_indicators = schema["principles"]["principle_6"]["indicators"]

    # ── 1. Scope 3 classification ────────────────────────────────────────────
    scope3_indicator = p6.get("e6_scope3_emissions", {})
    scope3_verdict   = _classify_scope3(scope3_indicator)
    scope3_verdict["maturity_signals"] = _extract_maturity_signals(scope3_indicator, p6)
    print(f"[analysis_layer] Scope 3 verdict: {scope3_verdict['level']}")

    # ── 2. Completeness assessment ───────────────────────────────────────────
    p6_completeness      = _assess_p6_completeness(p6, schema_indicators)
    completeness_results = [p6_completeness]
    print(
        f"[analysis_layer] P6 completeness: {p6_completeness['state']} "
        f"({p6_completeness['essential_disclosed']}/{p6_completeness['essential_total']} essential)"
    )

    # ── 3. Gap detection ─────────────────────────────────────────────────────
    gaps = _detect_gaps(p6, scope3_verdict, p6_completeness)
    print(f"[analysis_layer] Gaps detected: {len(gaps)}")
    for gap in gaps:
        print(f"  [{gap['severity'].upper():8}] {gap['gap_id']}: {gap['gap_name']}")

    return {
        "scope3_verdict":       scope3_verdict,
        "completeness_results": completeness_results,
        "gaps":                 gaps,
    }


def _empty_scope3_verdict() -> dict:
    """
    Safe fallback verdict for upstream failure or empty extraction.
    Prevents KeyError in downstream nodes that read scope3_verdict fields.
    """
    return {
        **_SCOPE3_LEVELS["not_found"],
        "evidence": "Extraction did not produce indicator data.",
        "citation": "Principle 6 — extraction incomplete",
        "maturity_signals": {
            "assurance":            "not_assessed",
            "category_boundary":    "not_assessed",
            "sbti":                 "not_found",
            "significant_partners": "not_assessed",
            "trend_data":           "not_assessed",
        },
    }