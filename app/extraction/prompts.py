"""
app/extraction/prompts.py

Prompt templates for LLM-based ESG indicator extraction.

This module is intentionally independent of:

- OpenAI
- LangGraph
- Pydantic

Its only responsibility is constructing prompts for the LLM.
"""

from textwrap import dedent


# ---------------------------------------------------------------------
# System Prompt
# ---------------------------------------------------------------------

SYSTEM_PROMPT = dedent("""
You are an expert ESG disclosure analyst.

Your task is to determine whether a requested ESG indicator is disclosed
using ONLY the supplied context.

Rules:

1. Never use outside knowledge.

2. Base every decision only on the retrieved context.

3. If the information is clearly present:
      state = "disclosed"

4. If some relevant information exists but the indicator is incomplete:
      state = "partially_disclosed"

5. If no evidence exists:
      state = "not_found"

6. Never invent values.

7. Evidence should be copied directly from the supplied context whenever possible.

8. Confidence must be between 0.0 and 1.0.

9. Return ONLY valid JSON.

10. The JSON MUST exactly follow this schema:

{
  "result": {
    "indicator_id": "...",
    "state": "disclosed | partially_disclosed | not_found",
    "value": "...",
    "evidence": "...",
    "citation": "...",
    "confidence": 0.95,
    "reasoning": "short explanation",
    "semantic_flags": {
      "scope3_mentioned": false,
      "scope3_has_absolute_number": false,
      "scope3_has_methodology": false,
      "scope3_is_intensity_only": false,
      "scope3_has_materiality_claim": false
    }
  }
}

The semantic_flags field is optional. Include it only when the user prompt
explicitly requests Scope 3 semantic flags; otherwise omit it.

Do not include markdown.

Do not include code fences.

Do not include additional text.
""")


# ---------------------------------------------------------------------
# User Prompt Template
# ---------------------------------------------------------------------

USER_PROMPT_TEMPLATE = dedent("""
Indicator ID:
{indicator_id}

Indicator Name:
{indicator_name}

Indicator Description:
{indicator_description}

Retrieved Context
-----------------
{context}

Instructions
------------

Determine whether this indicator is disclosed.

If disclosed:

- Extract the value.
- Extract supporting evidence.
- Extract the citation if available.

If not disclosed:

- Return an empty string for value.
- Return an empty string for evidence.
- Return an empty string for citation.

{semantic_flags_instructions}

Return ONLY valid JSON.
""")


SCOPE3_SEMANTIC_FLAGS_INSTRUCTIONS = dedent("""
Because this is the Scope 3 emissions indicator, include semantic_flags with
all five Boolean fields below. Set each field using ONLY the retrieved context:

- scope3_mentioned: true only if Scope 3, Scope III, or value-chain indirect
  emissions are explicitly mentioned.
- scope3_has_absolute_number: true only if an absolute Scope 3 quantity is
  reported (for example, a total tCO2e figure), not merely an intensity ratio.
- scope3_has_methodology: true only if a Scope 3 calculation or reporting
  methodology is explicitly named (for example, GHG Protocol or ISO 14064).
- scope3_is_intensity_only: true only if Scope 3 is reported as an intensity
  metric and no absolute Scope 3 quantity is reported.
- scope3_has_materiality_claim: true only if the context explicitly says Scope
  3 is immaterial, not relevant, not applicable, or makes an equivalent
  materiality/applicability claim.
""").strip()


NON_SCOPE3_SEMANTIC_FLAGS_INSTRUCTIONS = (
    "Do not include semantic_flags for this indicator."
)


# ---------------------------------------------------------------------
# Prompt Builder
# ---------------------------------------------------------------------

def build_extraction_prompt(
    *,
    indicator_id: str,
    indicator_name: str,
    indicator_description: str,
    context: str,
) -> str:
    """
    Build the user prompt for a single ESG indicator.

    Parameters
    ----------
    indicator_id:
        Unique indicator identifier.

    indicator_name:
        Human-readable indicator name.

    indicator_description:
        Definition of the ESG indicator.

    context:
        Retrieved document chunks relevant to this indicator.

    Returns
    -------
    str
        Prompt ready to send to the LLM.
    """

    semantic_flags_instructions = (
        SCOPE3_SEMANTIC_FLAGS_INSTRUCTIONS
        if indicator_id == "e6_scope3_emissions"
        else NON_SCOPE3_SEMANTIC_FLAGS_INSTRUCTIONS
    )

    return USER_PROMPT_TEMPLATE.format(
        indicator_id=indicator_id,
        indicator_name=indicator_name,
        indicator_description=indicator_description,
        context=context.strip(),
        semantic_flags_instructions=semantic_flags_instructions,
    )
