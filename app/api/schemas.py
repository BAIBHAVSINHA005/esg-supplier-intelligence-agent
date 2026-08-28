"""Public response models for the Supplier ESG Intelligence API."""

from typing import Literal

from pydantic import BaseModel, Field


class BriefHeader(BaseModel):
    supplier_name: str
    source_filename: str
    assessment_id: str
    generated_at: str
    confidence_level: Literal["high", "medium", "low"]
    confidence_directive: str
    hitl_flag: bool


class CompletenessItem(BaseModel):
    principle_number: int
    principle_name: str
    state: Literal["complete", "partial", "not_found", "unassessed"]
    citation: str
    essential_total: int
    essential_disclosed: int
    essential_partial: int
    essential_not_found: int
    essential_unassessed: int
    partial_indicators: list[str] = Field(default_factory=list)
    not_found_indicators: list[str] = Field(default_factory=list)
    unassessed_indicators: list[str] = Field(default_factory=list)
    leadership_disclosed: list[str] = Field(default_factory=list)


class Scope3PartialDetail(BaseModel):
    present: str
    missing: str


class Scope3MaturitySignals(BaseModel):
    assurance: Literal["found", "not_found", "not_assessed"]
    category_boundary: Literal["found", "not_found", "not_assessed"]
    sbti: Literal["found", "not_found", "not_assessed"]
    significant_partners: Literal["found", "not_found", "not_assessed"]
    trend_data: Literal["found", "not_found", "not_assessed"]


class Scope3Verdict(BaseModel):
    level: Literal[
        "not_found",
        "unassessed",
        "materiality_claim",
        "claim_only",
        "partial",
        "scope3_ready",
    ]
    level_number: int | None = None
    label: str
    evidence: str
    citation: str
    partial_detail: Scope3PartialDetail | None = None
    claim_detail: str | None = None
    maturity_signals: Scope3MaturitySignals | None = None


class Gap(BaseModel):
    rank: int
    gap_id: str
    gap_name: str
    brsr_reference: str
    severity: str
    description: str
    citation: str | None = None


class RecommendedAction(BaseModel):
    rank: int
    gap_id: str | None = None
    gap_name: str | None = None
    action: str


class ProcurementRecommendation(BaseModel):
    rank: int
    gap_id: str | None = None
    gap_name: str | None = None
    severity: str | None = None
    recommendation: str
    basis: str
    reference: str


class FollowUpQuestion(BaseModel):
    rank: int
    gap_id: str | None = None
    gap_name: str | None = None
    question: str
    linked_gap_id: str | None = None
    basis: str
    citation: str
    reference: str


class ExtractionError(BaseModel):
    indicator_id: str
    indicator_name: str
    error_code: str
    error_message: str
    citation: str


class EvidenceSourceLocation(BaseModel):
    page: int | None = None
    chunk_id: str | None = None
    retrieval_rank: int
    distance: float | None = None


class EvidenceEntry(BaseModel):
    indicator_id: str
    indicator_name: str
    state: Literal[
        "disclosed",
        "partially_disclosed",
        "not_found",
        "extraction_error",
    ]
    value: str | None = None
    evidence_excerpt: str | None = None
    citation: str
    raw_citation: str | None = None
    assessment_reference: str | None = None
    evidence_status: Literal[
        "source_matched",
        "citation_only",
        "excerpt_unmatched",
        "no_source_reference",
        "not_found",
        "extraction_error",
    ]
    source_locations: list[EvidenceSourceLocation] = Field(default_factory=list)
    extraction_method: str | None = None
    extraction_confidence: float | None = None
    error_code: str | None = None


class FinalBrief(BaseModel):
    executive_summary: str
    disclaimer: str
    header: BriefHeader
    completeness_assessment: list[CompletenessItem] = Field(default_factory=list)
    scope3_verdict: Scope3Verdict | None = None
    scope3_assessment_narrative: str
    confidence_explanation: str
    gaps: list[Gap] = Field(default_factory=list)
    gap_references: dict[str, str] = Field(default_factory=dict)
    recommended_actions: list[RecommendedAction] = Field(default_factory=list)
    procurement_recommendations: list[ProcurementRecommendation] = Field(
        default_factory=list
    )
    followup_questions: list[FollowUpQuestion] = Field(default_factory=list)
    question_references: dict[str, str] = Field(default_factory=dict)
    uncertain_fields: list[str] = Field(default_factory=list)
    extraction_errors: list[ExtractionError] = Field(default_factory=list)
    evidence_register: list[EvidenceEntry] = Field(default_factory=list)
    status: Literal["brief_generated"] | None = None
    error: str | None = None


class AssessmentEnvelope(BaseModel):
    brief: FinalBrief | None = None
    error: str | None = None
