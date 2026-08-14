"""Deterministic, supplier-specific follow-up question generation."""

from app.agent.state import AssessmentState
from app.agent.evidence import format_reference
from app.schemas.loader import get_indicators, load_schema


# Retained for callers that import the existing constant. Dynamic question
# generation below refines these themes using the actual pipeline findings.
QUESTION_LIBRARY = {
    "G-01": "Provide a complete Scope 3 inventory and supporting methodology.",
    "G-02": "Confirm the GHG accounting methodology and reporting boundary.",
    "G-03": "Provide the missing Principle 6 environmental disclosures.",
    "G-05": "Provide the climate or emissions-reduction target details.",
    "G-10": "Provide a GHG emissions-intensity metric.",
    "G-11": "Provide the Scope 3 leadership-indicator disclosure.",
}


def _p6_indicators(state: AssessmentState) -> dict:
    return state.get("extracted_indicators", {}).get("principle_6", {})


def _indicator_names() -> dict[str, str]:
    definitions = get_indicators(load_schema("brsr_v2023"), "principle_6")
    return {
        indicator_id: definition.get("name", indicator_id)
        for indicator_id, definition in definitions.items()
    }


def _join_items(items: list[str]) -> str:
    """Join business labels naturally without changing their content."""
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"


def _found_observations(p6: dict, indicator_ids: tuple[str, ...]) -> list[str]:
    """Describe only indicators that extraction actually found."""
    names = _indicator_names()
    observations = []
    for indicator_id in indicator_ids:
        result = p6.get(indicator_id, {})
        if result.get("state") not in ("disclosed", "partially_disclosed"):
            continue
        label = names.get(indicator_id, indicator_id)
        value = (result.get("value") or "").strip()
        observations.append(f"{label} ({value})" if value else label)
    return observations


def _question_for_gap(
    gap: dict,
    supplier_name: str,
    p6: dict,
    scope3_verdict: dict,
) -> tuple[str, str]:
    """Return question text and its deterministic finding basis."""
    gap_id = gap.get("gap_id")

    if gap_id == "G-01":
        level = scope3_verdict.get("level", "not_found")
        scope3_state = p6.get("e6_scope3_emissions", {}).get("state")
        if (
            level in ("unassessed", "extraction_error")
            or scope3_state == "extraction_error"
        ):
            finding = "Scope 3 could not be assessed because extraction failed."
            question = (
                f"{supplier_name}: {finding} Please identify the filing page or "
                "supporting document containing the Scope 3 disclosure so the source "
                "can be reviewed directly."
            )
            return question, finding
        if level == "claim_only":
            finding = (
                "Scope 3 was acknowledged, but no usable absolute inventory with "
                "methodology was identified."
            )
        elif level == "materiality_claim":
            finding = (
                "The filing states that Scope 3 is not material or applicable, "
                "without a quantified inventory or supporting assessment."
            )
        else:
            finding = "No Scope 3 disclosure was identified in the uploaded BRSR."
        question = (
            f"{supplier_name}: {finding} Please provide the latest Scope 3 inventory, "
            "including the reporting period, absolute tCO2e, categories covered, "
            "organizational and operational boundaries, calculation methodology, "
            "and supporting calculations."
        )
        return question, finding

    if gap_id == "G-02":
        reported = _found_observations(
            p6, ("e6_scope1_emissions", "e6_scope2_emissions")
        )
        if reported:
            finding = (
                f"The filing reports {_join_items(reported)}, but no GHG accounting "
                "methodology was identified."
            )
        else:
            finding = "No GHG accounting methodology was identified in the filing."
        question = (
            f"{supplier_name}: {finding} Please confirm the standard or protocol, "
            "reporting period and boundary, emissions factors, and assurance status "
            "used for the reported emissions."
        )
        return question, finding

    if gap_id == "G-03":
        names = _indicator_names()
        missing = [
            names.get(indicator_id, indicator_id)
            for indicator_id, result in p6.items()
            if result.get("state") == "not_found"
            and indicator_id != "e6_scope3_emissions"
        ]
        if missing:
            missing_text = _join_items(missing)
            finding = f"The filing did not disclose {missing_text}."
            request = f"Please provide the latest reporting-period data for {missing_text}"
        else:
            finding = "Principle 6 environmental disclosure was severely incomplete."
            request = "Please provide the missing Principle 6 environmental data"
        question = (
            f"{supplier_name}: {finding} {request}, including units, reporting "
            "boundaries, and supporting source documentation."
        )
        return question, finding

    if gap_id == "G-05":
        finding = (
            "No climate or emissions-reduction target was identified in the filing."
        )
        question = (
            f"{supplier_name}: {finding} Please provide any current target, including "
            "its baseline year, target year, emissions scopes, boundary, interim "
            "milestones, and implementation status."
        )
        return question, finding

    if gap_id == "G-10":
        reported = _found_observations(
            p6, ("e6_scope1_emissions", "e6_scope2_emissions")
        )
        reported_text = _join_items(reported)
        if reported_text:
            finding = (
                f"The filing reports {reported_text}, but no GHG intensity metric was "
                "identified."
            )
        else:
            finding = "No GHG intensity metric was identified in the filing."
        question = (
            f"{supplier_name}: {finding} Please provide the corresponding intensity "
            "metric, denominator, reporting period, and calculation basis."
        )
        return question, finding

    if gap_id == "G-11":
        finding = "The Scope 3 leadership indicator was not addressed in the filing."
        question = (
            f"{supplier_name}: {finding} Please provide the current Scope 3 reporting "
            "boundary, categories assessed, latest available data, and data-collection "
            "plan."
        )
        return question, finding

    finding = (
        "The assessment identified this gap: "
        f"{gap.get('gap_name', 'Disclosure gap')}."
    )
    return (
        f"{supplier_name}: {finding} Please provide the relevant disclosure and "
        "supporting source documentation.",
        finding,
    )


def generate_questions(state: AssessmentState) -> dict:
    """Generate supplier-facing questions from existing gaps and findings."""
    gaps = state.get("gaps", [])
    supplier_name = state.get("supplier_name") or "Supplier"
    p6 = _p6_indicators(state)
    scope3_verdict = state.get("scope3_verdict", {})

    print(
        f"[generate_questions] Building follow-up questions from "
        f"{len(gaps)} gap(s)"
    )

    questions = []
    for gap in gaps:
        question_text, basis = _question_for_gap(
            gap, supplier_name, p6, scope3_verdict
        )
        gap_id = gap.get("gap_id")
        reference = format_reference(
            gap.get("citation"), gap.get("brsr_reference")
        )
        questions.append(
            {
                "rank": gap.get("rank", len(questions) + 1),
                "gap_id": gap_id,
                "gap_name": gap.get("gap_name"),
                "question": question_text,
                "linked_gap_id": gap_id,
                "basis": basis,
                "citation": reference,
                "reference": reference,
            }
        )

    print(
        f"[generate_questions] Generated "
        f"{len(questions)} follow-up question(s)"
    )

    return {"followup_questions": questions}
