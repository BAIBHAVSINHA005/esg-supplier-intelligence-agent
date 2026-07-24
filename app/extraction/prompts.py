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
    "reasoning": "short explanation"
  }
}

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

Return ONLY valid JSON.
""")


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

    return USER_PROMPT_TEMPLATE.format(
        indicator_id=indicator_id,
        indicator_name=indicator_name,
        indicator_description=indicator_description,
        context=context.strip(),
    )