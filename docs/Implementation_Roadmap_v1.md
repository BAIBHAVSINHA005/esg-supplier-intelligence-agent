# Supplier ESG Intelligence Agent
# Implementation Roadmap v1

**Audience:** Recruiters, hiring managers, technical reviewers, sustainability/procurement stakeholders, and prospective clients

**Goal:** Ship a portfolio-quality V1 demonstrating evidence-grounded BRSR intelligence, LangGraph orchestration, RAG, deterministic ESG analysis, API delivery, and containerized execution.
**Status:** Core intelligence complete; delivery layer pending
**Updated:** August 2026

---

## 1. V1 Objective

V1 converts a machine-readable Indian BRSR filing into a procurement-ready ESG Intelligence Brief.

The product focus is intentionally narrow:

- BRSR only
- Principle 6 depth
- Scope 3 procurement readiness
- evidence traceability
- disclosure gaps
- supplier follow-up questions
- procurement recommendations

V1 is not intended to be a full ESG platform. It is an end-to-end, auditable portfolio MVP with a stable service boundary and realistic reliability controls.

---

## 2. Current V1 Scope

### Included

| Capability | V1 status |
| --- | --- |
| PDF ingestion | Complete |
| BRSR detection / quality checks | Complete |
| supplier name extraction with filename fallback | Complete |
| Chroma indexing | Complete |
| document-scoped retrieval | Complete |
| indicator-specific retrieval | Complete |
| structured LLM extraction | Complete |
| deterministic Scope 3 analysis | Complete |
| Principle 6 completeness | Complete |
| ESG gap detection | Complete |
| confidence + HITL | Complete |
| evidence register / provenance | Complete |
| supplier-specific follow-up questions | Complete |
| procurement recommendations | Complete |
| Streamlit UI | Complete |
| Gradio UI | Complete |
| FastAPI | Pending |
| OpenAPI / Swagger | Pending |
| Docker | Pending |
| final release packaging | Pending |

### Explicitly deferred beyond V1

- persistence / assessment history
- Supabase / PostgreSQL
- pgvector migration
- authentication
- multi-user support
- multi-supplier comparison
- supplier email sending
- procurement-system integrations
- MCP
- multi-agent orchestration
- GraphRAG / knowledge graph
- GRI / CSRD / ISSB / CDP support
- full nine-principle depth

---

## 3. Implemented Workflow

```text
Upload BRSR PDF
    ->
ingest_document
    ->
index_document
    ->
quality_check
    ->
retrieve_context
    ->
extract_indicators
    ->
analysis_layer
    ->
assess_confidence
    ->
generate_questions
    ->
compile_brief
    ->
Streamlit / Gradio output
```

The shared supplier-assessment service is the application boundary.

FastAPI will call the same service rather than duplicating LangGraph or ESG logic.

---

## 4. Completed Engineering Phases

### Phase 1 — LangGraph foundation

Completed:

- `AssessmentState`
- node / edge mental model
- conditional routing
- graph compilation and invocation
- small text-quality learning pipeline
- separation of node responsibilities

Learning outcome:

> LangGraph is being used as workflow orchestration, not as a reason to make every step autonomous.

### Phase 2 — PDF ingestion and quality

Completed:

- PyMuPDF ingestion
- page/text extraction
- BRSR / Principle 6 detection
- document-readability checks
- failure routing
- supplier metadata extraction

Current supplier-name precedence:

```text
explicit user name
    ->
Name of the Listed Entity from Section A
    ->
filename-derived fallback
```

The filename is not treated as authoritative company identity.

### Phase 3 — Structured ESG extraction

Completed:

- structured indicator schema
- Pydantic-validated LLM outputs
- Principle 6 indicator extraction
- explicit disclosure states
- semantic flags needed by downstream analysis

Current extraction states include:

- `disclosed`
- `partially_disclosed`
- `not_found`
- `extraction_error`

### Phase 4 — RAG integration and hardening

Completed:

- ChromaDB
- `all-MiniLM-L6-v2`
- document-specific indexing
- `document_id` isolation
- top-5 retrieval per indicator
- indicator-specific queries
- bounded chunk subdivision
- retrieval regression tests

Important design change:

The current RAG system retrieves **supplier document evidence** for each target indicator. It is not the originally planned framework-knowledge RAG architecture.

### Phase 5 — Deterministic ESG analysis

Completed:

- Scope 3 readiness classification
- Principle 6 completeness
- deterministic gap rules
- severity / business-significance logic
- recommendation mapping

Representative Scope 3 outcomes:

```text
Not Found
Claim Only
Materiality Claim
Partial
Ready / sufficiently disclosed
```

The classification is intentionally more useful than a binary disclosed/not-disclosed flag.

### Phase 6 — Reliability controls

Completed:

- `not_found` separated from `extraction_error`
- extraction errors suppress false ESG gaps
- LOW confidence + HITL on failed extraction
- targeted OpenAI rate-limit retry/backoff
- no retries for unrelated failures
- Scope 3 state-contract guard
- regression coverage for reliability failures

### Phase 7 — Evidence grounding

Completed:

- `evidence_register`
- strict normalized evidence matching
- source/page/chunk metadata where matchable
- `source_matched`
- `citation_only`
- `excerpt_unmatched`
- `not_found`
- no fabricated evidence for missing disclosures

### Phase 8 — Procurement-facing output

Completed:

- executive summary
- confidence explanation
- Scope 3 narrative
- completeness assessment
- critical gaps
- supplier-specific follow-up questions
- deterministic procurement recommendations
- expandable Evidence Details
- Streamlit / Gradio presentation

---

## 5. Real-Document Validation

### Reliance Industries

Validated behavior:

- document-isolated retrieval
- total waste generated correctly recovered after chunking hardening
- Scope 3 correctly remains `not_found`
- HIGH confidence
- one grounded critical Scope 3 gap
- no false gaps from extraction errors

### Birla Corporation Limited

Validated behavior:

- supplier name extracted from the PDF
- Scope 3 absolute emissions: `18,09,403.78 tCO2e`
- Scope 3 classified as Partial because usable accounting methodology was not identified
- total waste generated: `31,223.96 MT`
- evidence and procurement recommendations grounded to current findings

### Current automated baseline

```text
47 passed
0 failed
```

The suite covers retrieval, chunking, document isolation, state semantics,
evidence grounding, supplier naming, confidence/HITL, recommendations, and
failure paths.

---

## 6. Major Reliability Lessons Incorporated into V1

### 6.1 Retrieval false negative from oversized chunks

Observed:

- Reliance waste disclosure existed in the source
- the correct page was indexed
- embedding representation lost late-page content
- correct evidence missed top-5

Fix:

- subdivide oversized chunks into small overlapping windows

### 6.2 State-contract inconsistency

Observed:

- extraction returned Scope 3 `not_found`
- semantic flag `scope3_mentioned=true`
- analysis promoted result to `claim_only`

Fix:

- primary extraction state remains authoritative
- materiality claim is the deliberate exception

### 6.3 Over-broad indicator queries

Observed in Birla:

- correct Scope 3 chunk ranked 12
- correct Total Waste Generated chunk ranked 9
- semantically related but wrong passages occupied top-5

Fix:

- narrow indicator queries to standardized target-row wording
- keep `k=5`

### 6.4 Evidence-selection ambiguity

Observed:

- recovered waste total could be mistaken for generated waste when only the wrong retrieval context was available

Fix:

- improve retrieval specificity rather than making evidence matching fuzzy

---

## 7. Current Learning Map

### Skills already exercised

#### Python
- `TypedDict`
- dictionaries / structured state
- pure functions
- error handling
- file / byte processing
- modular design
- testing

#### LangGraph
- state
- nodes
- edges
- conditional routing
- graph compilation
- workflow orchestration

#### RAG
- chunking
- embeddings
- ChromaDB
- metadata filtering
- top-k retrieval
- retrieval-query design
- retrieval regression testing
- provenance

#### LLM application engineering
- structured extraction
- Pydantic validation
- prompt constraints
- retry handling
- deterministic post-processing
- separating model failure from business absence

#### Product engineering
- service layer
- Streamlit / Gradio
- evidence-grounded UX
- procurement recommendations
- HITL
- multi-company validation

### Next learning required for V1

#### FastAPI
- request/response models
- file uploads
- routers
- synchronous vs asynchronous routes
- OpenAPI / Swagger
- service boundaries

#### Docker
- Dockerfile
- dependency installation
- environment variables
- exposing application ports
- reproducible local execution

---

## 8. Remaining V1 Delivery Plan

### Phase 9 — FastAPI

Goal:

Expose the existing supplier-assessment service through an HTTP API without changing the intelligence pipeline.

Implementation requirements:

1. define a Pydantic request/input boundary
2. define an explicit Pydantic brief response model
3. add a PDF assessment endpoint
4. call the existing supplier-assessment service
5. do not duplicate business logic in routes
6. handle synchronous LangGraph execution safely

Preferred simple V1 approach:

- use a synchronous FastAPI route (`def`) for the blocking assessment call,
  unless async behavior is actually needed

Acceptance criteria:

- upload a BRSR PDF through Swagger
- receive the structured brief as JSON
- success and controlled-failure responses conform to documented schemas
- Streamlit behavior remains unchanged

### Phase 10 — OpenAPI / Swagger validation

Validate:

- file upload contract
- response schema
- optional fields
- error/failure model
- example assessment execution
- no schema mismatch between brief and API response

### Phase 11 — Docker

Goal:

Package V1 reproducibly.

Acceptance criteria:

```text
docker build
    ->
docker run
    ->
FastAPI starts
    ->
Swagger opens
    ->
BRSR assessment succeeds
```

Do not add Docker Compose or infrastructure services unless they are required.

### Phase 12 — Final validation

Before release:

1. run full automated suite
2. rerun Reliance
3. rerun Birla
4. test one weaker / disclosure-poor BRSR
5. validate API response
6. validate Docker execution
7. run `git diff --check`

### Phase 13 — Portfolio release

Complete:

- final README
- final Architecture v1
- final V1 Status
- architecture diagram
- representative screenshots
- setup/run instructions
- `.env.example`
- clean Git status
- release commit/tag

---

## 9. V1 Acceptance Criteria

### Document processing

- [x] machine-readable BRSR PDF can be ingested
- [x] BRSR / Principle 6 content can be located
- [x] unreadable documents fail safely

### Retrieval

- [x] chunks are isolated by `document_id`
- [x] indicator-specific context is retrieved
- [x] oversized chunks are bounded
- [x] retrieval regressions exist for known false negatives

### Extraction

- [x] nine Principle 6 indicators are assessed
- [x] output is structurally validated
- [x] technical failure is not represented as absence

### Analysis

- [x] Scope 3 readiness is deterministically classified
- [x] completeness is calculated
- [x] procurement-relevant gaps are identified
- [x] recommendations derive from existing findings

### Evidence

- [x] evidence register is produced
- [x] source references are preserved when matchable
- [x] missing evidence is not fabricated

### User output

- [x] executive brief is readable
- [x] supplier questions are specific
- [x] detailed provenance is secondary/expandable
- [x] supplier name is resolved from reliable metadata

### Reliability

- [x] extraction errors force appropriate confidence/HITL behavior
- [x] rate limits use bounded retry
- [x] maintained automated suite is green

### Delivery

- [ ] FastAPI endpoint implemented
- [ ] Pydantic API contract validated
- [ ] Swagger assessment run completed
- [ ] Docker build/run validated
- [ ] third real-company validation completed
- [ ] final V1 docs/screenshots completed
- [ ] V1 tagged/released

---

## 10. Post-V1 Direction

### V2 — persistent multi-supplier product

Business goal:

Move from a single-document assessment to repeated supplier assessment and supplier-data follow-up.

Potential capabilities:

- PostgreSQL / Supabase
- assessment history
- multi-supplier views
- supplier-response workflow
- retrieval evaluation / LangSmith / RAGAS
- MCP exposure of stable assessment capabilities
- authentication if justified

### V3 — controlled agentic supplier workflows

Business goal:

Support suppliers with incomplete or heterogeneous evidence.

Potential specialist roles:

- Disclosure Agent
- Evidence Agent
- Framework Agent
- Supplier Gap / Outreach Agent
- Procurement Agent
- Independent Verifier / Critic

The deterministic ESG rules remain authoritative underneath the agent layer.

### V4 — enterprise Scope 3 intelligence

Potential capabilities:

- multi-year supplier history
- supplier benchmarking
- broader ESG frameworks
- buyer-supplier portfolio analysis
- framework mappings
- graph relationships / GraphRAG when justified
- enterprise procurement integrations

---

## 11. Current Execution Decision

Do not add major product features before V1 release.

The current sequence is:

```text
FastAPI
    ->
OpenAPI / Swagger
    ->
Docker
    ->
third-company validation
    ->
final documentation / demo
    ->
V1 release
```

The purpose of the remaining V1 work is delivery and packaging, not another feature-expansion sprint.
