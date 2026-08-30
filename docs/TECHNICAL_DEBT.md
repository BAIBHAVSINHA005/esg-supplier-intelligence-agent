# Supplier ESG Intelligence Agent
# Technical Debt

This document tracks **known implementation limitations or engineering work that remains desirable after V1**.

It intentionally excludes:
- product features deliberately deferred to V2+
- capabilities that are merely optional enhancements
- issues already fixed during V1

The purpose is to keep technical debt distinct from roadmap scope.

---

## 1. Retrieval and RAG

### 1.1 Formal retrieval evaluation

**Status:** Open
**Priority:** Medium

Current retrieval quality has been improved through real-document regression cases, but there is not yet a formal benchmark dataset with precision/recall-style evaluation across all target indicators.

Future work:
- create a small gold-standard retrieval set
- record expected evidence chunks per indicator
- measure top-k hit rate
- compare retrieval changes before accepting them

### 1.2 Hybrid retrieval / reranking

**Status:** Deferred unless evaluation justifies it
**Priority:** Low

The current dense retrieval pipeline works adequately after:
- bounded chunk subdivision
- document isolation
- indicator-specific queries

Hybrid BM25+dense retrieval or reranking should only be added if evaluation shows a consistent retrieval gap.

This is therefore **not a V1 blocker**.

### 1.3 Collection lifecycle and cleanup

**Status:** Open
**Priority:** Medium

The application uses document-scoped metadata filtering, which prevents cross-document retrieval contamination.

However, long-running use may still benefit from:
- explicit cleanup of old document embeddings
- expiry policy
- collection-size monitoring
- persistent document lifecycle management

This becomes more important once assessments are stored persistently.

---

## 2. Extraction

### 2.1 Numeric and table robustness

**Status:** Partially mitigated
**Priority:** Medium

Real BRSR filings frequently contain:
- Indian-number formatting
- table rows split across lines
- repeated totals
- generated vs recovered waste values
- units separated from values

Current retrieval and structured extraction handle tested cases, but broader numeric robustness should be evaluated on more companies and sectors.

Future work:
- more table-focused regression fixtures
- unit normalization
- numeric normalization
- explicit row-label/value pairing tests

### 2.2 Methodology extraction

**Status:** Open for broader validation
**Priority:** Medium

GHG accounting methodology can appear in:
- table footnotes
- narrative disclosures
- standards references
- separate sustainability sections

The current system correctly preserves `not_found` when methodology is not identified, but broader validation is needed to reduce false negatives.

### 2.3 Sequential LLM extraction

**Status:** Known limitation
**Priority:** Low for V1

Indicator extraction currently executes sequentially.

Potential future improvements:
- bounded concurrency
- async execution where justified
- batch extraction experiments

Do not optimize until API behavior, rate limits, and reliability are measured.

---

## 3. Evidence and Provenance

### 3.1 Page reference availability

**Status:** Known limitation
**Priority:** Low

Strict evidence matching may sometimes produce:
- `citation_only`
- `excerpt_unmatched`

rather than a fully `source_matched` record with page/chunk metadata.

The current design intentionally prefers incomplete provenance over fabricated provenance.

Future work:
- improve citation-to-page reconciliation
- preserve additional PDF structural metadata during ingestion

### 3.2 Evidence-quality scoring

**Status:** Future enhancement
**Priority:** Low

The Evidence Register currently records match state, but does not expose a formal evidence-quality score.

A future score could incorporate:
- exact source match
- page availability
- retrieval rank
- structured row-label alignment

This is not required for V1.

---

## 4. Confidence and HITL

### 4.1 HITL remains advisory

**Status:** Intentional V1 limitation
**Priority:** V2

Current behavior:

```text
LOW confidence
    ->
HITL flag
    ->
brief still returned with warning
```

There is no persistent analyst review queue, approval state, or corrected-assessment workflow.

Future implementation may include:
- review queue
- analyst approval/rejection
- evidence correction
- reassessment history

### 4.2 Confidence calibration

**Status:** Open
**Priority:** Medium

Current confidence logic is deterministic and useful for V1, but has not been statistically calibrated against a labeled evaluation set.

Future work:
- define confidence test cases
- compare confidence level against manual-review outcomes
- adjust thresholds only from evidence

---

## 5. API and Delivery

### 5.1 FastAPI and Docker delivery boundary

**Status:** Implemented and validated locally
**Priority:** Closed for V1

The API and containerization work previously tracked here is complete:

- `GET /health` and multipart `POST /v1/assessments`
- explicit nested Pydantic public response contract
- OpenAPI / Swagger validation
- synchronous LangGraph execution behind the shared service boundary
- Python 3.12 Docker build with CPU-only PyTorch
- Uvicorn container startup and HTTP 200 health check
- successful real Birla BRSR assessment inside the container

Cloud deployment is remaining V1 release work, not completed technical debt.

### 5.2 Single-worker, synchronous assessment execution

**Status:** Intentional V1 limitation
**Priority:** V2, based on measured demand

The container runs one Uvicorn worker and each assessment performs blocking
LangGraph/LLM work. This is acceptable for the V1 portfolio workflow. Before
supporting concurrent production traffic, evaluate request queuing, worker
isolation, timeouts, and ChromaDB concurrency behavior.

---

## 6. Persistence and Multi-User Concerns

### 6.1 No persistent assessment store

**Status:** Intentionally deferred
**Priority:** V2

V1 is a single-assessment workflow.

Future persistence may include:
- PostgreSQL / Supabase
- supplier records
- assessment history
- evidence records
- versioned reassessments

### 6.2 No authentication / authorization

**Status:** Intentionally deferred
**Priority:** V2

Authentication is unnecessary for the local portfolio V1.

It becomes required before:
- multi-user deployment
- persistent supplier data
- external client use

---

## 7. Evaluation and Observability

### 7.1 No formal RAG evaluation framework

**Status:** Open
**Priority:** V2

Current evaluation is regression-test and real-document driven.

Future options:
- RAGAS
- custom retrieval metrics
- gold-standard datasets

### 7.2 Limited runtime observability

**Status:** Open
**Priority:** V2

Current logs are sufficient for local development, but a production-oriented version would benefit from:
- LangSmith tracing
- structured logs
- latency tracking
- token/cost tracking
- per-node failure analytics

---

## 8. Items Removed from Earlier Technical Debt

The following were previously listed as debt but are now materially addressed.

### Document isolation
Earlier concern:
- clear the collection or use document-specific collections

Current solution:
- shared collection
- UUID `document_id`
- retrieval filtered by active document

### Chunk metadata
Earlier concern:
- add section / table / chunk metadata

Current system now preserves richer retrieval metadata including document,
page, chunk, rank, and matching context where available.

### Retrieval quality
Earlier concern:
- generic retrieval quality

Current mitigations:
- bounded chunk subdivision
- indicator-specific queries
- real-document regression tests

### Waste extraction
Earlier concern:
- improve waste parsing

Current status:
- known Reliance and Birla waste failures were diagnosed and fixed
- broader generalization still belongs under numeric/table robustness, not as an unresolved known bug

---

## 9. Debt Prioritization

### Must close before V1 release
- maintained regression validation
- final documentation and release hardening
- third weaker-BRSR validation if retained
- cloud deployment
- `v1.0.0` release/tag

### Important after V1
- formal retrieval evaluation
- confidence calibration
- broader table/numeric regression coverage
- collection lifecycle management
- runtime observability
- checkpointing/persistence

### Add only if evidence justifies it
- hybrid retrieval
- reranking
- async/concurrent extraction
- GraphRAG

The project should avoid converting every possible enhancement into technical debt.
