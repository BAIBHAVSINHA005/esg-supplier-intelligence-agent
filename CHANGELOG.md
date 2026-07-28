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