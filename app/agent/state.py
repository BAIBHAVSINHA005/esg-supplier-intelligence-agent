# app/agent/state.py

from typing import TypedDict, Optional, Literal, List, Dict, Any


class AssessmentState(TypedDict):
    """
    The single shared state object for the ESG Intelligence Agent pipeline.

    Every node reads from this dict and writes back a subset of these fields.
    LangGraph merges each node's returned dict into this state automatically.
    No node should ever return fields it did not write — only return your changes.

    Fields are grouped by which node is responsible for writing them.
    Fields are NEVER deleted from state — only added or updated.
    """

    # ── GROUP 1: INPUT ─────────────────────────────────────────────────────
    # Set by the caller before graph.invoke(). Never written by any node.

    assessment_id: str
    # A unique identifier for this assessment run.
    # Placeholder: "test-001"
    # Future: UUID generated in app/utils/storage.py before invoke() is called.
    # Used to: link brief output to a stored assessment record.

    supplier_name: str
    # The name of the company whose BRSR is being assessed.
    # Placeholder: "Test Supplier Ltd"
    # Future: entered by the analyst in the Streamlit upload form.
    # Used to: personalise follow-up questions and appear in the brief header.

    source_filename: str
    # Original filename of the uploaded PDF.
    # Placeholder: "test_brsr.pdf"
    # Future: captured from st.file_uploader in the Streamlit UI.
    # Used to: appear in the brief disclaimer and assessment record.

    document_bytes: bytes
    # Raw binary content of the uploaded PDF file.
    # Placeholder: b""  (empty bytes — no real file in Phase 2)
    # Future: populated from st.file_uploader's .read() method.
    # Used by: ingest_document node only — passes bytes to PyMuPDF.

    # ── GROUP 2: INGESTION ─────────────────────────────────────────────────
    # Written by: ingest_document

    document_text: str
    # Full extracted text from the PDF, all pages concatenated.
    # Placeholder: "PLACEHOLDER: full PDF text will appear here."
    # Future: PyMuPDF page.get_text() for every page, joined together.
    # Used by: quality_check (to find BRSR section), extract_indicators (for RAG chunking).

    document_chunks: List[Dict]
    # The document split into smaller pieces with metadata.
    # Placeholder: []
    # Future: list of dicts, each containing:
    #   {"text": "...", "page": 45, "section": "Principle 6", "is_table": False}
    # Used by: the RAG layer to index into ChromaDB for retrieval during extraction.

    num_pages: int
    # Total number of pages in the PDF.
    # Placeholder: 0
    # Future: len(fitz.open(stream=document_bytes)) from PyMuPDF.
    # Used by: quality_check to calculate characters-per-page as a readability signal.

    # ── GROUP 3: QUALITY CHECK ─────────────────────────────────────────────
    # Written by: quality_check

    is_machine_readable: bool
    # True if the PDF has extractable text (not scanned/image-only).
    # Placeholder: True
    # Future: calculated from chars_per_page threshold (< 200 chars/page = likely scanned).
    # Used by: assess_confidence to set confidence level; routing to detect failure.

    brsr_section_found: bool
    # True if the BRSR chapter was located within the document.
    # Placeholder: True
    # Future: heuristic search for BRSR section markers in document_text.
    # Used by: routing (document_failure path); assess_confidence.

    brsr_section_text: str
    # Extracted text of the BRSR section only — not the full annual report.
    # Placeholder: "PLACEHOLDER: BRSR section text will appear here."
    # Future: sliced from document_text starting at BRSR section header.
    # Used by: extract_indicators (source text for Claude extraction calls).

    extraction_confidence_score: float
    # Raw score 0.0–1.0 reflecting document quality before level assignment.
    # Placeholder: 0.9
    # Future: calculated from readability + section detection + BRSR content depth.
    # Used by: assess_confidence to assign High / Medium / Low level.

    document_failure: bool
    # True if the document cannot be processed at all.
    # Placeholder: False
    # Future: True when is_machine_readable=False OR brsr_section_found=False.
    # Used by: route_after_quality_check — the only field that drives routing.

    document_failure_reason: Optional[str]
    # Human-readable explanation of why processing failed.
    # Placeholder: None
    # Future: e.g. "Document appears to be scanned. Text extraction failed."
    # Used by: handle_failure node to populate brief["error"].

    # ── GROUP 4: EXTRACTION ────────────────────────────────────────────────
    # Written by: extract_indicators

    extracted_indicators: Dict[str, Any]
    # Structured extraction of BRSR indicator data from the document.
    # Placeholder: {}
    # Future structure:
    # {
    #   "principle_6": {
    #     "scope_1_emissions": {
    #       "state": "disclosed",           # disclosed | partially_disclosed | not_found
    #       "value": "12,450 tCO2e",
    #       "citation": "Principle 6, Essential Indicator E-7, Page 142"
    #     },
    #     "scope_3_emissions": {
    #       "state": "not_found",
    #       "value": "",
    #       "citation": "Not found in uploaded BRSR filing — Principle 6, Indicator E-8 checked"
    #     }
    #   }
    # }
    # Used by: analysis_layer (all three classifiers read this).

    # ── GROUP 5: ANALYSIS ──────────────────────────────────────────────────
    # Written by: analysis_layer

    scope3_verdict: Dict[str, Any]
    # The classified Scope 3 readiness verdict with evidence.
    # Placeholder: {}
    # Future structure:
    # {
    #   "level": "not_found",             # not_found | claim_only | partial | scope3_ready | materiality_claim
    #   "evidence": "No Scope 3 data found in Principle 6 tables.",
    #   "citation": "Not found in uploaded BRSR filing — Principle 6, Indicator E-8 checked",
    #   "maturity_signals": {
    #     "assurance": "not_found",
    #     "category_boundary": "not_found",
    #     "sbti": "not_found",
    #     "significant_partners": "not_found",
    #     "trend_data": "not_found"
    #   }
    # }
    # Used by: assess_confidence; compile_brief; gap_detector (G-01 trigger).

    completeness_results: List[Dict]
    # Per-principle completeness states for all nine BRSR principles.
    # Placeholder: []
    # Future: list of 9 dicts, one per BRSR principle:
    # [
    #   {
    #     "principle_number": 6,
    #     "principle_name": "Environment",
    #     "state": "partial",             # complete | partial | not_found
    #     "citation": "Section C, Principle 6, Pages 140–148",
    #     "partial_indicators": ["scope_3_emissions", "water_intensity"]
    #   }
    # ]
    # Used by: compile_brief; gap_detector.

    gaps: List[Dict]
    # The top five procurement-relevant disclosure gaps, ranked by severity.
    # Placeholder: []
    # Future: list of up to 5 dicts:
    # [
    #   {
    #     "rank": 1,
    #     "gap_id": "G-01",
    #     "gap_name": "Scope 3 not disclosed",
    #     "brsr_reference": "Principle 6, Essential Indicator E-8",
    #     "severity": "critical",
    #     "description": "Supplier has not disclosed Scope 3 emissions...",
    #     "citation": "Not found in uploaded BRSR filing — Principle 6, Indicator E-8 checked"
    #   }
    # ]
    # Used by: generate_questions (derives questions from gaps); compile_brief.

    # ── GROUP 6: CONFIDENCE ────────────────────────────────────────────────
    # Written by: assess_confidence

    confidence_level: Literal["high", "medium", "low"]
    # Named confidence level derived from extraction_confidence_score and extraction results.
    # Placeholder: "low"
    # Future: "high" if score >= 0.8 AND extraction ratio >= 0.8 AND no uncertain fields.
    #         "medium" if score >= 0.5 AND extraction ratio >= 0.5.
    #         "low" otherwise.
    # Used by: compile_brief (brief header); Streamlit UI (confidence banner colour).

    confidence_directive: str
    # The full human-facing directive telling the analyst how to use this brief.
    # Placeholder: "PLACEHOLDER: directive will appear here."
    # Future: one of three fixed strings defined in nodes/confidence.py.
    # Used by: compile_brief; Streamlit confidence_banner component.

    hitl_flag: bool
    # True when the brief requires human review before being acted on.
    # Placeholder: False
    # Future: True when confidence_level == "low" OR uncertain_fields count > 2.
    # Used by: compile_brief (brief header); Streamlit UI (HITL banner); storage.
    # Note: does NOT change routing — it is a field that propagates to the output,
    #       not a gate that stops the pipeline.

    uncertain_fields: List[str]
    # Names of specific fields where extraction confidence was low.
    # Placeholder: []
    # Future: e.g. ["principle_6.scope_3_emissions", "principle_5.human_rights_policy"]
    # Used by: compile_brief to render [⚠] markers on affected fields in the brief.

    # ── GROUP 7: OUTPUT ────────────────────────────────────────────────────
    # Written by: generate_questions and compile_brief

    followup_questions: List[Dict]
    # Three to five supplier-facing follow-up questions generated from gaps.
    # Placeholder: []
    # Future: list of up to 5 dicts:
    # [
    #   {
    #     "rank": 1,
    #     "question": "Your BRSR filing for FY2023–24 does not include...",
    #     "linked_gap_id": "G-01"
    #   }
    # ]
    # Used by: compile_brief.

    brief: Optional[Dict]
    # The fully assembled ESG Intelligence Brief — the final product of the pipeline.
    # Placeholder: None (written by compile_brief or handle_failure at the very end)
    # Future: a structured dict containing all brief sections,
    #         serialisable to JSON for storage and display in Streamlit.
    # Used by: Streamlit brief_viewer page; utils/storage.py for JSON persistence.

    error: Optional[str]
    # Set only on the failure path. Human-readable failure description.
    # Placeholder: None
    # Future: populated by handle_failure from document_failure_reason.
    # Used by: compile_brief and Streamlit to display the failure message.


def make_initial_state(
    supplier_name: str,
    source_filename: str = "test_brsr.pdf",
    document_bytes: bytes = b"",
    document_failure: bool = False,
) -> dict:
    """
    Helper that builds a fully-initialised state dict.
    Every TypedDict field must be present at invoke() time.
    """

    return {
        # Input
        "assessment_id": "test-001",
        "supplier_name": supplier_name,
        "source_filename": source_filename,
        "document_bytes": document_bytes,

        # Ingestion
        "document_text": "",
        "document_chunks": [],
        "num_pages": 0,

        # Quality check
        "is_machine_readable": False,
        "brsr_section_found": False,
        "brsr_section_text": "",
        "extraction_confidence_score": 0.0,
        "document_failure": document_failure,
        "document_failure_reason": None,

        # Extraction
        "extracted_indicators": {},

        # Analysis
        "scope3_verdict": {},
        "completeness_results": [],
        "gaps": [],

        # Confidence
        "confidence_level": "low",
        "confidence_directive": "",
        "hitl_flag": False,
        "uncertain_fields": [],

        # Output
        "followup_questions": [],
        "brief": None,
        "error": None,
    }