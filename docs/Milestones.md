# Supplier ESG Intelligence Agent
# Milestones

This document records the **actual implementation history** of the project.
It is intentionally different from `Implementation_Roadmap_v1.md`, which
describes the delivery plan.

---

## Milestone 1 — LangGraph Foundation

**Status:** ✅ Completed
**Period:** June 2026

### Completed
- Built the initial LangGraph learning pipeline
- Implemented shared `TypedDict` state
- Added nodes, edges, and conditional routing
- Tested successful and failure branches
- Connected OpenAI-based summarisation in the learning sandbox

### Key Learning
The project established LangGraph as the workflow orchestration layer before
adding ESG-specific complexity.

---

## Milestone 2 — MVP-2: End-to-End RAG Pipeline

**Status:** ✅ Completed
**Date:** July 2026

### Completed
- PDF ingestion and document parsing
- Chunk enhancement with UUID-based chunk IDs
- ChromaDB indexing integrated into LangGraph
- Semantic retrieval from uploaded documents
- ESG indicator extraction
- Analysis layer
- Confidence assessment
- Follow-up question generation
- ESG Intelligence Brief compilation
- End-to-end LangGraph execution verified

### Key Engineering Fixes
- Added explicit `index_document` node to the graph
- Fixed missing indexing before retrieval
- Integrated chunk enhancement into the ingestion pipeline
- Eliminated stale vector retrieval behavior

### Technical Debt Identified at the Time
- numeric/table extraction needed improvement
- retrieval quality needed stronger validation
- collection lifecycle management needed refinement
- evaluation metrics were not yet formalized

---

## Milestone 3 — Reliability Sprint: Extraction Failure Semantics

**Status:** ✅ Completed
**Commit:** `352c80c`

### Problem
Transient LLM/API failures were being represented as `not_found`.

This created a serious business risk:

```text
API failure
    ->
indicator marked missing
    ->
false ESG disclosure gap
```

### Completed
- Introduced distinct `extraction_error`
- Added structured error code/message handling
- Prevented extraction failures from creating ESG gaps
- Forced LOW confidence when extraction errors exist
- Triggered HITL on extraction failure
- Made essential-indicator completeness `unassessed` where appropriate
- Added UI warnings for unassessed indicators
- Added bounded rate-limit retry behavior
- Added regression tests

### Engineering Decision
`not_found` now means the assessment completed and no qualifying disclosure was
identified. `extraction_error` means the assessment itself could not be
completed reliably.

---

## Milestone 4 — Analyst-Focused Brief Presentation

**Status:** ✅ Completed
**Commit:** `d766102`

### Completed
- Added `executive_summary`
- Added Scope 3 assessment narrative
- Added confidence explanation
- Improved business-language presentation
- Added clearer "Why it matters" framing
- Updated Streamlit and Gradio
- Added tests

### Product Outcome
The output shifted from a technical workflow result toward an analyst- and
procurement-facing intelligence brief.

---

## Milestone 5 — Evidence Grounding and Supplier Questions

**Status:** ✅ Completed
**Commit:** `4777409`

### Completed
- Added `evidence_register`
- Added strict evidence-to-retrieved-chunk grounding
- Preserved page/chunk/rank/distance metadata only when supportable
- Added evidence states:
  - `source_matched`
  - `citation_only`
  - `excerpt_unmatched`
  - `not_found`
- Prevented fabricated evidence
- Kept `extraction_error` semantically distinct
- Added supplier-specific follow-up questions
- Linked questions to detected gaps
- Updated Streamlit and Gradio to expose provenance
- Added evidence-grounding tests

### Engineering Decision
Evidence matching uses deterministic normalization rather than fuzzy semantic
matching.

The system prefers an incomplete citation over a fabricated source reference.

---

## Milestone 6 — Retrieval Hardening: Reliance Waste False Negative

**Status:** ✅ Completed

### Problem
The Reliance BRSR contained the correct value for Total Waste Generated:

```text
9,93,787 metric tonnes
```

but the production top-5 retrieval did not surface the correct passage.

### Diagnosis
- the correct page existed in Chroma
- the target passage ranked outside top-5
- a large page-like chunk was approximately 6,852 characters
- the embedding model's effective representation truncated later content

### Fix
- subdivided oversized chunks into approximately 60-token windows
- added approximately 15-token overlap
- preserved source/page/document metadata
- left small chunks unchanged
- kept production top-k unchanged
- added a retrieval regression test

### Outcome
The Reliance waste disclosure moved into usable top-5 retrieval after reindexing.

### Learning
A source fact can be present in the PDF and correctly indexed while still being
effectively invisible to retrieval because of embedding representation limits.

---

## Milestone 7 — Scope 3 State-Contract Fix

**Status:** ✅ Completed

### Problem
An extraction could return:

```text
state = not_found
scope3_mentioned = true
```

The downstream classifier used the semantic flag and incorrectly promoted the
result to `claim_only`.

### Fix
The primary extraction state was made authoritative:

```text
not_found
    ->
remain not_found
```

unless a specifically defined materiality claim is present.

### Regression Coverage
- `not_found + mentioned=true -> not_found`
- `not_found + materiality claim -> materiality_claim`
- `partially_disclosed + mentioned -> claim_only`

### Learning
Retrieval and extraction can be correct while a downstream state transformation
still creates an incorrect business conclusion.

---

## Milestone 8 — Sprint 6: Procurement Guidance and UI Polish

**Status:** ✅ Completed

### Completed
- Added deterministic procurement recommendations
- Grounded recommendations in existing gaps/findings/evidence
- Improved Streamlit hierarchy
- Kept detailed provenance in expandable Evidence Details
- Improved Gradio presentation
- Added supplier-name handling
- Added tests for recommendations and UI/service behavior

### Product Outcome
The system now produces a decision sequence closer to a procurement analyst's
workflow:

```text
Executive Summary
    ->
Scope 3 Verdict
    ->
Evidence
    ->
Gap
    ->
Supplier Question
    ->
Procurement Recommendation
```

---

## Milestone 9 — Cross-Company Validation: Birla Retrieval Generalization

**Status:** ✅ Completed

### Validation Document
Birla Corporation Limited BRSR FY2025-26

### Initial Problems
The first run incorrectly returned:

- Scope 3: `not_found`
- waste evidence: `31,176.75` MT, which was total waste recovered rather than
  total waste generated
- GHG methodology: `not_found`
- climate/emissions target: `not_found`

### Diagnosis
The source data and chunking were correct.

The remaining issue was retrieval-query specificity.

For Scope 3:
- correct chunk initially ranked 12

For Total Waste Generated:
- correct chunk initially ranked 9
- recovered-waste passage ranked above it

### Fix
Narrowed only the relevant retrieval queries to standardized BRSR row language.

Production `k=5` was retained.

### Outcome
The corrected assessment retrieved:

- Scope 3 emissions: `18,09,403.78 tCO2e`
- Total Waste Generated: `31,223.96 MT`

Scope 3 was classified **Partial**, not `not_found`, because the absolute value
was disclosed but an acceptable accounting methodology was not identified.

### Learning
Broad semantic queries can be weaker than precise standardized regulatory row
language for structured filings.

---

## Milestone 10 — Supplier Metadata Resolution

**Status:** ✅ Completed

### Problem
A filename-derived label such as:

```text
Birla Corporation Limited Brsr202526
```

is not a professional supplier identity.

### Completed
Supplier-name resolution now uses:

```text
1. explicit user-supplied supplier name
2. "Name of the Listed Entity" from BRSR Section A
3. filename-derived fallback
```

### Outcome
The brief now consistently presents:

```text
Birla Corporation Limited
```

rather than the raw filename-derived label.

---

## Milestone 11 — Current V1 Validation Baseline

**Status:** ✅ Core intelligence complete

### Automated Tests

```text
57 passed
0 failed
11 subtests passed
```

### Real-Document Validation Completed
- Reliance Industries
- Birla Corporation Limited

### Current V1 Capabilities
- machine-readable BRSR ingestion
- Principle 6 extraction
- document-scoped RAG
- indicator-specific retrieval
- deterministic Scope 3 readiness
- evidence provenance
- confidence / HITL
- supplier-specific questions
- procurement recommendations
- Streamlit / Gradio presentation

---

## Milestone 12 — V1 API and Container Delivery

**Status:** ✅ Completed locally

### Completed

- FastAPI `GET /health`
- multipart PDF `POST /v1/assessments`
- explicit nested Pydantic public response contract
- OpenAPI and Swagger upload validation
- Docker image build on Python 3.12
- CPU-only PyTorch dependency setup
- Uvicorn/FastAPI container startup
- container `/health` HTTP 200
- real Birla BRSR assessment through Swagger, FastAPI, Docker, LangGraph,
  RAG/LLM, and typed brief output
- maintained regression suite: 57 passed, 0 failed, 11 subtests passed

### Outcome

The local Dockerized V1 path is verified end to end. Cloud deployment is not
part of this completed milestone and has not yet been claimed.

---

## Milestone 13 — V1 Release Closure

**Status:** In progress

### Remaining

- maintained regression validation
- final documentation, demo assets, and release hardening
- one additional weaker/disclosure-poor BRSR validation, if retained
- cloud deployment and deployed endpoint verification
- final release commit and `v1.0.0` tag

### Current Execution Order

```text
regression validation
    ->
documentation / release hardening
    ->
third weaker-BRSR validation (if retained)
    ->
cloud deployment
    ->
v1.0.0 release/tag
```

---

## Key Project-Level Learning

The strongest engineering lesson from V1 is that a wrong AI output does not
automatically mean "the prompt is bad."

The diagnostic sequence used throughout the project is:

```text
source fact present?
    ->
ingestion correct?
    ->
chunk / embedding representation correct?
    ->
retrieval correct?
    ->
model received the right evidence?
    ->
structured extraction correct?
    ->
state transformation correct?
    ->
business analysis correct?
    ->
UI presentation correct?
```

This sequence has become one of the central engineering practices of the
project.
