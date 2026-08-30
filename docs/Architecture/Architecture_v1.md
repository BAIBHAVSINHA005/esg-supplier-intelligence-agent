# Supplier ESG Intelligence Agent

## Architecture v1

**Status:** Current V1 Architecture — Local Containerized Delivery Verified
**Version:** 1.0
**Updated:** August 2026

---

## 1. Purpose

The Supplier ESG Intelligence Agent converts a machine-readable Indian
Business Responsibility and Sustainability Report (BRSR) into an
evidence-grounded, procurement-ready ESG Intelligence Brief.

V1 intentionally focuses on **BRSR Principle 6: Environment**, with special
attention to whether supplier climate disclosures are sufficiently complete
and traceable for Scope 3 procurement and due-diligence use.

The architecture separates:

- document processing and retrieval,
- structured LLM extraction,
- deterministic ESG/business rules,
- confidence and HITL controls,
- evidence/provenance,
- service and presentation layers.

The system is designed so that presentation technologies do not contain ESG
decision logic.

---

## 2. V1 Architecture Principles

### 2.1 Domain logic stays outside the UI

Streamlit and Gradio are presentation layers only. Core intelligence is
implemented in the shared service, LangGraph workflow, extraction layer, RAG
layer, and deterministic analysis functions.

FastAPI consumes the same service layer through a thin HTTP boundary.

### 2.2 Deterministic rules complement LLM extraction

The LLM extracts structured facts from retrieved evidence.

Deterministic logic then handles:

- disclosure completeness,
- Scope 3 classification,
- gap creation,
- severity,
- confidence consequences,
- procurement recommendation mapping.

This avoids asking the LLM to make every business decision.

### 2.3 Missing disclosure is different from failed extraction

The system preserves a strict distinction between:

- `not_found` — assessment completed but no qualifying disclosure was found
- `extraction_error` — assessment could not be completed reliably

An extraction failure must not create a false ESG gap.

### 2.4 Evidence must remain auditable

Evidence excerpts are linked back to retrieved document chunks where possible.
The system prefers incomplete provenance over fabricated provenance.

### 2.5 Retrieval is document-scoped and indicator-specific

Every indexed chunk carries a `document_id`. Retrieval is filtered to the
active document to prevent cross-supplier contamination.

Queries are tailored to individual BRSR indicators because standardized
regulatory row labels can be more useful than broad semantic queries.

### 2.6 V1 is intentionally BRSR-focused

V1 does not attempt to be framework-agnostic.

BRSR Principle 6 depth is preferred over premature support for GRI, CSRD,
ISSB, CDP, or other frameworks. Multi-framework support is deferred until the
BRSR workflow is stable and evaluated.

---

## 3. Current V1 Technology Stack

| Layer | Current V1 implementation | Role |
| --- | --- | --- |
| User interfaces | Streamlit + Gradio | Upload and display of ESG Intelligence Briefs |
| HTTP API | FastAPI + Uvicorn | Health and multipart assessment endpoints |
| Public API contract | Explicit nested Pydantic models | OpenAPI/Swagger request and response schema |
| Shared application boundary | Python service layer | Single entry point for assessment execution |
| Workflow orchestration | LangGraph | State, nodes, routing, assessment workflow |
| LLM extraction | OpenAI Responses API + Pydantic validation | Structured indicator extraction |
| PDF processing | PyMuPDF | Text extraction and page metadata |
| Embeddings | `all-MiniLM-L6-v2` | Local document embeddings |
| Vector retrieval | ChromaDB | Document-scoped semantic retrieval |
| Analysis | Deterministic Python rules | Scope 3 classification, completeness, gaps, actions |
| Evidence layer | Deterministic provenance matching | Evidence register and source references |
| Packaging | Docker on Python 3.12 with CPU-only PyTorch | Reproducible local API runtime |
| Tests | `pytest` maintained suite | Reliability and regression validation |

### Remaining before V1 release

| Layer | Remaining V1 work |
| --- | --- |
| Deployment | Cloud deployment and deployed endpoint verification |
| Release | Final hardening and `v1.0.0` tag |

Persistence, authentication, Supabase/PostgreSQL, pgvector, MCP, and
multi-agent orchestration are **not current V1 dependencies**.

---

## 4. High-Level System Architecture

```text
                 +----------------------+
                 | Client / Swagger     |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 | FastAPI + Pydantic   |
                 | in Docker / Uvicorn  |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 | Supplier Assessment  |
                 | Service Layer        |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 |      LangGraph       |
                 |  Workflow Engine     |
                 +----------+-----------+
                            |
       +--------------------+--------------------+
       |                    |                    |
       v                    v                    v
+-------------+      +-------------+      +-------------+
| PDF / BRSR  |      | RAG /       |      | Structured  |
| Processing  |      | ChromaDB    |      | Extraction  |
+-------------+      +-------------+      +-------------+
       |                    |                    |
       +--------------------+--------------------+
                            |
                            v
                 +----------------------+
                 | Deterministic ESG    |
                 | Analysis + Evidence  |
                 +----------+-----------+
                            |
                            v
                 +----------------------+
                 | ESG Intelligence     |
                 | Brief                |
                 +----------------------+
```

### Verified FastAPI boundary

```text
External API Client
        |
        v
FastAPI + nested Pydantic contract
        |
        v
Supplier Assessment Service
        |
        v
     LangGraph
```

For V1, Streamlit and Gradio continue to call the shared service directly.
FastAPI is an additional consumer of the same service contract and runs under
Uvicorn inside Docker for the verified container path.

This avoids duplicating domain logic and keeps the API boundary independent of
the user interface.

---

## 5. Current LangGraph Workflow

The V1 success path is:

```text
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
```

Failure routing stops the workflow when the document is unreadable or required
BRSR content cannot be assessed safely.

---

## 6. Shared Assessment State

`AssessmentState` carries workflow data between LangGraph nodes.

Representative state includes:

- source filename
- document bytes/text
- page count
- document chunks
- BRSR/Principle 6 content
- retrieved context per indicator
- extracted indicators
- analysis results
- confidence score/level
- HITL flag
- follow-up questions
- executive brief
- error information

State is used for workflow coordination. Persistent multi-user storage is
outside V1 scope.

---

## 7. Document Ingestion and Metadata

### `ingest_document`

Responsibilities:

- parse the uploaded PDF with PyMuPDF,
- extract machine-readable text,
- capture page-level metadata,
- derive core document metadata,
- locate relevant BRSR content.

Supplier name resolution uses this precedence:

```text
1. Explicit user-supplied supplier name
2. "Name of the Listed Entity" extracted from BRSR Section A
3. Filename-derived fallback
```

The filename is therefore not treated as authoritative company identity.

---

## 8. Chunking and Indexing

### Problem discovered during validation

A real Reliance BRSR waste disclosure was initially missed because a large
page-like chunk exceeded the useful representation window of the embedding
model.

### Current approach

Oversized chunks are subdivided into approximately:

- 60-token windows
- 15-token overlap

while preserving:

- `document_id`
- page number
- source filename
- parent chunk identity
- chunk position metadata

Small chunks remain unchanged.

### `index_document`

Chunks are embedded and added to a shared Chroma collection.

Each assessment receives a unique `document_id`, which is attached to all
indexed chunks.

---

## 9. Retrieval Architecture

### Document isolation

All retrieval is filtered by active `document_id`.

Conceptually:

```python
where={"document_id": document_id}
```

This prevents stale or previously indexed supplier content from contaminating
the active assessment.

### Indicator-specific retrieval

The workflow retrieves context separately for nine Principle 6 indicators:

1. Total Energy Consumption
2. Scope 1 GHG Emissions
3. Scope 2 GHG Emissions
4. GHG Accounting Methodology
5. GHG Emission Intensity
6. Scope 3 GHG Emissions
7. Climate or Emissions Reduction Target
8. Water Consumption
9. Total Waste Generated

Production retrieval currently uses **top-5 chunks per indicator**.

### Query precision lesson

Cross-company validation showed that broad ESG terminology can hurt retrieval
precision in standardized BRSR tables.

Examples:

- a broad Scope 3 query ranked generic climate/value-chain passages above the
  actual Scope 3 disclosure row;
- a broad waste query ranked waste recovered above Total Waste Generated.

The current queries therefore prefer the standardized target-row language for
indicators where precision matters.

---

## 10. Structured LLM Extraction

### `extract_indicators`

For each indicator:

1. receive only its retrieved top-5 chunks,
2. construct bounded extraction context,
3. call the OpenAI model,
4. validate the structured response with Pydantic,
5. store disclosure state and evidence.

The LLM does **not** receive the entire report.

### Extraction states

Important states include:

- `disclosed`
- `partially_disclosed`
- `not_found`
- `extraction_error`

`extraction_error` is reserved for technical/validation failures and remains
semantically distinct from genuine absence.

---

## 11. OpenAI Failure and Retry Handling

Only `RateLimitError` is retried.

The policy:

1. respect API-provided retry/reset timing where available,
2. parse requested wait time when needed,
3. add a safety buffer,
4. use exponential backoff only when no server delay is available,
5. stop after three total attempts.

Unrelated errors are not retried indiscriminately.

After final failure, the indicator becomes `extraction_error`, not `not_found`.

---

## 12. Deterministic ESG Analysis

### `analysis_layer`

The analysis layer converts extracted facts into business-facing conclusions.

Responsibilities include:

- Principle 6 completeness,
- Scope 3 readiness classification,
- ESG gap detection,
- severity assignment,
- deterministic procurement implications.

### Scope 3 semantics

V1 uses graded semantics rather than a binary yes/no disclosure flag.

Representative outcomes include:

```text
Not Found
Claim Only
Materiality Claim
Partial
Ready / sufficiently disclosed
```

A quantitative Scope 3 figure without the required supporting methodology may
be classified as **Partial**, because the number exists but is not yet fully
comparable or ready for buyer-side decision use.

The extraction state remains authoritative. A qualitative flag cannot silently
promote an extraction state of `not_found`, except for specifically defined
materiality-claim behavior.

---

## 13. Confidence and Human-in-the-Loop

### `assess_confidence`

Confidence reflects **assessment reliability**, not supplier ESG performance.

Inputs include:

- document quality,
- essential-indicator coverage,
- extraction uncertainty/failure.

Representative behavior:

- strong document + high essential coverage -> HIGH
- incomplete but usable assessment -> MEDIUM
- extraction failure -> LOW + HITL

### HITL in V1

HITL remains advisory:

```text
LOW confidence
      ->
HITL flag
      ->
brief still returned with warning
```

A persistent review queue is deferred.

---

## 14. Evidence and Provenance

The evidence layer creates an `evidence_register` for extracted indicators.

Evidence status may include:

- `source_matched`
- `citation_only`
- `excerpt_unmatched`
- `not_found`

Matching uses deterministic normalization and strict containment rather than
fuzzy semantic matching.

Normalization handles common PDF extraction artifacts such as:

- whitespace,
- line-wrap hyphens,
- Unicode ligatures/subscripts,
- quote variants,
- dash variants,
- punctuation spacing.

### Design rule

For a genuine `not_found` result:

- no evidence excerpt is fabricated,
- no page number is fabricated,
- the brief uses a controlled absence reference.

Detailed provenance is shown in secondary/expandable Evidence Details rather
than cluttering the primary decision brief.

---

## 15. Supplier Questions and Procurement Recommendations

### `generate_questions`

Follow-up questions are generated from **existing structured gaps**, not from
free-form brainstorming.

Questions are supplier-specific and reference the underlying gap/finding.

### `compile_brief`

The brief includes deterministic procurement recommendations grounded only in:

- existing gaps,
- existing findings,
- existing evidence/references.

This prevents recommendation generation from inventing new ESG findings.

The intended decision hierarchy is:

```text
Executive Summary
      ->
Scope 3 Verdict
      ->
Interpretation
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

## 16. User Interfaces

### Streamlit

Primary recruiter/demo interface.

Responsibilities:

- PDF upload
- optional supplier name
- assessment execution
- executive brief display
- confidence/HITL display
- procurement recommendations
- gaps/questions
- expandable evidence details

### Gradio

Legacy/secondary interface retained for compatibility and demonstration.

Neither UI owns ESG decision logic.

---

## 17. FastAPI Implementation in V1

FastAPI is implemented as a thin delivery boundary with `GET /health` and
multipart `POST /v1/assessments`.

### 17.1 Blocking LangGraph execution

The current LangGraph workflow is synchronous and can take tens of seconds.

V1 must avoid calling the blocking workflow directly inside an `async def`
route.

The implemented V1 approach is:

- define the assessment endpoint with synchronous `def`, allowing FastAPI to
  execute it in its thread pool.

### 17.2 Explicit API contract

FastAPI responses use explicit nested Pydantic models reflecting the existing
brief structure.

The API schema should model the **current implemented output**, including
optional/partial-failure fields, rather than inventing a future ideal schema.

### 17.3 One service contract

FastAPI, Streamlit, and Gradio must use the same supplier-assessment service
logic.

No ESG or LangGraph business rule should be duplicated inside API routes.

---

## 18. Current Validation Baseline

### Automated tests

The maintained suite currently has:

```text
57 passed
0 failed
11 subtests passed
```

Coverage includes:

- retrieval regressions
- document isolation
- chunk subdivision
- Scope 3 state consistency
- `not_found` vs `extraction_error`
- confidence/HITL
- retry behavior
- evidence grounding
- procurement recommendations
- supplier-name extraction/fallback

### Real-document validation

#### Reliance Industries

Validated behavior includes:

- total waste generated correctly retrieved,
- Scope 3 correctly remains `not_found`,
- high-confidence assessment,
- no false gaps from extraction failures.

#### Birla Corporation Limited

Validated behavior includes:

- legal supplier name extracted from Section A,
- Scope 3 absolute emissions retrieved as `18,09,403.78 tCO2e`,
- Scope 3 classified Partial because methodology was not identified,
- total waste generated retrieved as `31,223.96 MT`,
- grounded procurement gaps and questions.

A third weaker/disclosure-poor BRSR may be retained before V1 closure to
exercise additional real-world paths.

---

## 19. V1 Boundaries

### Included in V1

- machine-readable BRSR PDFs
- Principle 6 depth
- single-document assessment
- RAG with ChromaDB
- structured extraction
- deterministic ESG analysis
- Scope 3 readiness
- evidence provenance
- confidence/HITL
- supplier questions
- procurement recommendations
- Streamlit / Gradio
- FastAPI / OpenAPI with multipart PDF upload
- Docker/Uvicorn runtime on Python 3.12 with CPU-only PyTorch

### Explicitly deferred

- PostgreSQL / Supabase persistence
- pgvector migration
- authentication
- multi-user assessment history
- other ESG frameworks
- supplier email sending
- procurement system integrations
- MCP
- autonomous multi-agent orchestration
- GraphRAG / knowledge graph

These are deferred to keep V1 focused and auditable.

---

## 20. Post-V1 Architectural Direction

### V2 — Reliability, persistence, and multi-supplier operation

Expected concerns:

- PostgreSQL / Supabase
- assessment history
- SQLAlchemy / migrations where needed
- LangSmith observability
- RAGAS/retrieval evaluation
- authentication
- MCP exposure of stable assessment capabilities
- supplier-response workflow

### V3 — Controlled agentic workflows

Specialist agents may be introduced only where they represent genuinely
different responsibilities and tools.

Potential roles:

```text
ESG Orchestrator
     |
     +--> Disclosure Agent
     +--> Evidence Agent
     +--> Framework Agent
     +--> Gap / Supplier Outreach Agent
     +--> Procurement Agent
     `--> Independent Verifier / Critic
```

The validated deterministic ESG rules remain underneath these agents rather
than being replaced by an unconstrained autonomous system.

### V4 — Enterprise Scope 3 intelligence

Possible later capabilities:

- broader ESG frameworks
- multi-year supplier history
- supplier benchmarking
- buyer-supplier portfolio analysis
- cross-framework mapping
- graph relationships / GraphRAG when relational use cases justify it
- enterprise integrations

---

## 21. Architecture Status

```text
Core V1 intelligence pipeline       COMPLETE
Reliability hardening               COMPLETE
Evidence / procurement layer        COMPLETE
Real-company validation             COMPLETE FOR RELIANCE + BIRLA
FastAPI / OpenAPI                   COMPLETE
Dockerized local execution          COMPLETE
Real Birla Docker assessment        COMPLETE
Cloud deployment                    NOT COMPLETE
Final documentation + hardening     IN PROGRESS
v1.0.0 release/tag                  NOT COMPLETE
```

The current architecture is deliberately conservative: it prioritizes
traceable decisions and a stable service boundary before persistence,
integrations, or multi-agent expansion.
