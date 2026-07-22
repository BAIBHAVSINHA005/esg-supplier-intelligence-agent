"""
app/extraction/schemas.py

Pydantic models for the LLM extraction layer.

These models define the contract between:

LLM
 ↓
extract_indicators
 ↓
analysis_layer
 ↓
confidence
 ↓
brief generation

Every LLM extraction must conform to these models.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------
# Allowed disclosure states
# ---------------------------------------------------------------------

DisclosureState = Literal[
    "disclosed",
    "partially_disclosed",
    "not_found",
]


# ---------------------------------------------------------------------
# Result for ONE indicator
# ---------------------------------------------------------------------

class IndicatorExtractionResult(BaseModel):
    """
    Structured extraction result for a single ESG indicator.
    """

    indicator_id: str = Field(
        description="Unique indicator identifier from the schema."
    )

    state: DisclosureState = Field(
        description="Disclosure state determined by the LLM."
    )

    value: str = Field(
        default="",
        description="Extracted quantitative value if available."
    )

    evidence: str = Field(
        default="",
        description="Supporting text snippet from retrieved context."
    )

    citation: str = Field(
        default="",
        description="Citation or page reference if available."
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Model confidence between 0 and 1."
    )

    reasoning: Optional[str] = Field(
        default=None,
        description="Short internal explanation of why this classification was chosen."
    )


# ---------------------------------------------------------------------
# Internal result returned by the extractor
# ---------------------------------------------------------------------

class ExtractionResponse(BaseModel):
    """
    Internal wrapper returned by the LLM extractor.
    """

    result: IndicatorExtractionResult


# ---------------------------------------------------------------------
# Conversion helper
# ---------------------------------------------------------------------

def to_pipeline_dict(
    result: IndicatorExtractionResult,
) -> dict:
    """
    Convert a validated Pydantic object into the dictionary format
    already expected by the existing pipeline.

    This preserves compatibility with:

    - analysis_layer
    - assess_confidence
    - compile_brief
    """

    return {
        "indicator_id": result.indicator_id,
        "state": result.state,
        "value": result.value,
        "evidence": result.evidence,
        "citation": result.citation,
        "extraction_method": "llm",
        "confidence": result.confidence,
        "uncertain": False,
    }


# ---------------------------------------------------------------------
# Error result helper
# ---------------------------------------------------------------------

def make_error_result(
    indicator_id: str,
    citation: str = "",
) -> dict:
    """
    Standard fallback result used when the LLM call fails.

    This keeps downstream nodes running without raising exceptions.
    """

    return {
        "indicator_id": indicator_id,
        "state": "not_found",
        "value": "",
        "evidence": "",
        "citation": citation,
        "extraction_method": "llm",
        "confidence": 0.0,
        "uncertain": True,
    }