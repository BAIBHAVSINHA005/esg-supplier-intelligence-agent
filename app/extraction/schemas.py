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
    "extraction_error",
]


# ---------------------------------------------------------------------
# Optional semantic metadata
# ---------------------------------------------------------------------

class IndicatorSemanticFlags(BaseModel):
    """Optional indicator-specific semantics for downstream business rules.

    The model keeps semantic interpretation separate from the core disclosure
    fields so that future indicator families can add metadata without changing
    the primary extraction contract.
    """

    scope3_mentioned: bool = Field(
        default=False,
        description="Whether the context explicitly mentions Scope 3 emissions.",
    )

    scope3_has_absolute_number: bool = Field(
        default=False,
        description="Whether Scope 3 is reported as an absolute quantity.",
    )

    scope3_has_methodology: bool = Field(
        default=False,
        description="Whether a Scope 3 calculation or reporting methodology is named.",
    )

    scope3_is_intensity_only: bool = Field(
        default=False,
        description="Whether Scope 3 is reported only as an intensity metric.",
    )

    scope3_has_materiality_claim: bool = Field(
        default=False,
        description="Whether the context makes a Scope 3 materiality or applicability claim.",
    )


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

    semantic_flags: Optional[IndicatorSemanticFlags] = Field(
        default=None,
        description="Optional indicator-specific semantic metadata for downstream rules.",
    )

    error_code: Optional[str] = Field(
        default=None,
        description="Machine-readable extraction failure code when state is extraction_error.",
    )

    error_message: Optional[str] = Field(
        default=None,
        description="Extraction failure detail when state is extraction_error.",
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

    Semantic flags remain available as nested metadata and are also flattened
    when present for existing deterministic analysis rules.
    """

    semantic_flags = (
        result.semantic_flags.model_dump()
        if result.semantic_flags is not None
        else None
    )

    pipeline_result = {
        "indicator_id": result.indicator_id,
        "state": result.state,
        "value": result.value,
        "evidence": result.evidence,
        "citation": result.citation,
        "semantic_flags": semantic_flags,
        "extraction_method": "llm",
        "confidence": result.confidence,
        "uncertain": False,
        "error_code": result.error_code,
        "error_message": result.error_message,
    }

    if semantic_flags is not None:
        pipeline_result.update(semantic_flags)

    return pipeline_result


# ---------------------------------------------------------------------
# Error result helper
# ---------------------------------------------------------------------

def make_error_result(
    indicator_id: str,
    citation: str = "",
    error_code: str = "extraction_error",
    error_message: str = "",
) -> dict:
    """
    Standard fallback result used when the LLM call fails.

    This keeps downstream nodes running without raising exceptions.
    """

    return {
        "indicator_id": indicator_id,
        "state": "extraction_error",
        "value": "",
        "evidence": "",
        "citation": citation,
        "extraction_method": "llm",
        "confidence": 0.0,
        "uncertain": True,
        "error_code": error_code,
        "error_message": error_message,
    }
