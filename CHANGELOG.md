# Changelog

All notable changes to this project are documented here.

---

## v0.3.1 (2026-07-28)

### Added
- Semantic metadata (`semantic_flags`) for ESG extraction.
- Enhanced extraction prompts.
- Backward-compatible pipeline mapping.
- Regression tests for semantic flags.

### Improved
- Better downstream support for deterministic analysis.

### Validation
- Verified end-to-end extraction on real BRSR reports.

### Known Limitation
- Retrieval currently uses a shared Chroma collection without document-level filtering.
- Cross-document retrieval contamination was identified during validation.
- Planned resolution: document-scoped retrieval (MVP 3.1.5).


## MVP 3.1.5 (2026-07-29)

### Improved
- Implemented document-level retrieval isolation in ChromaDB using `document_id` metadata.
- Added UUID-based `document_id` generation to LangGraph state.
- Propagated `document_id` through the indexing and retrieval pipeline.
- Updated Chroma retrieval to filter results using metadata:
  `where={"document_id": document_id}`.
- Preserved separation between `assessment_id` (business workflow) and `document_id` (retrieval infrastructure).

### Migration
- Removed the legacy `esg_document_chunks` collection because previously indexed vectors did not contain `document_id` metadata.
- Re-indexing is required after upgrading to this version.



### Validation

- Successfully validated document-level retrieval isolation using multiple ESG reports.
- Confirmed retrieved chunks contain the active `document_id`.
- Verified end-to-end LangGraph execution after retrieval enhancement.