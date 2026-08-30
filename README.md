# Supplier ESG Intelligence Agent

An evidence-grounded AI workflow that converts an Indian supplier's Business
Responsibility and Sustainability Report (BRSR) into a procurement-ready ESG
Intelligence Brief.

Built as a portfolio project for applied AI, document intelligence, and agentic
workflow engineering, it combines RAG, structured LLM extraction, deterministic
ESG rules, evidence grounding, and explicit reliability controls.

The goal is not to replace analyst judgement. It is to help procurement and
sustainability teams answer a more practical question:

> **Can this supplier's disclosed ESG data be used reliably for Scope 3
> reporting, supplier due diligence, and procurement follow-up?**

## V1 status

The core V1 intelligence workflow is implemented and validated on real BRSR
filings.

Current V1 work includes:

- BRSR Principle 6 document intelligence
- indicator-specific RAG retrieval
- structured LLM extraction
- deterministic ESG and Scope 3 analysis
- confidence and human-in-the-loop (HITL) controls
- evidence provenance and source matching
- supplier-specific follow-up questions
- deterministic procurement recommendations
- Streamlit and Gradio presentation layers
- FastAPI `GET /health` and multipart `POST /v1/assessments` endpoints
- explicit nested Pydantic response models exposed through OpenAPI/Swagger
- a Python 3.12 Docker image with CPU-only PyTorch and Uvicorn
- verified real-BRSR assessments through the complete Dockerized API path
- regression tests for retrieval, state consistency, grounding, and failure paths

The remaining V1 work is release-focused: **maintained regression validation,
final documentation and release hardening, cloud deployment, and the `v1.0.0`
release/tag**. Cloud deployment and the final release/tag are not yet complete.

## Why it matters

Supplier sustainability filings contain decision-relevant information, but it
is often buried in long PDFs and reported inconsistently. A buyer needs more
than a text summary. It needs to know:

- whether the disclosure is actually present,
- whether the extracted value is traceable to evidence,
- whether a missing disclosure is different from a failed extraction,
- whether Scope 3 information is usable or only partially usable,
- what information should be requested from the supplier next.

The application therefore produces a structured ESG Intelligence Brief rather
than a generic document summary.

## Current assessment scope

The current release accepts machine-readable BRSR PDFs and assesses
**BRSR Principle 6: Environment** across nine indicators:

| Area | Indicators |
| --- | --- |
| Energy and emissions | Total energy consumption; Scope 1 and Scope 2 GHG emissions; GHG accounting methodology; GHG emissions intensity |
| Value-chain climate data | Scope 3 GHG emissions (leadership indicator); climate or emissions-reduction target |
| Resources and waste | Water consumption; total waste generated |

The intended use cases are supplier onboarding, procurement risk assessment,
Scope 3 data collection, and ESG due diligence.

### Scope 3 decision semantics

The system does not treat Scope 3 as simply disclosed or not disclosed.
It distinguishes whether the available information is sufficiently complete for
buyer-side decision use.

Examples include:

- **Not Found** — no qualifying Scope 3 disclosure identified
- **Claim Only** — qualitative acknowledgement without usable quantitative data
- **Partial** — some usable information exists, but a required disclosure element
  such as methodology is missing
- **Ready / sufficiently disclosed** — quantitative disclosure and supporting
  context are available for decision use
- **Materiality Claim** — a specific materiality statement exists even when a
  quantitative inventory is not disclosed

This allows the workflow to answer a procurement-oriented question:
**"Can the buyer actually use this supplier's data?"**

## How it works

```text
API client / Swagger
        |
        v
FastAPI + nested Pydantic contract
        |
        v
supplier assessment service
        |
        v
compiled LangGraph workflow
        |
        +--> PDF ingestion and metadata extraction
        +--> size-bounded chunking and Chroma indexing
        +--> document quality and BRSR checks
        +--> document-scoped, indicator-specific retrieval
        +--> structured LLM indicator extraction
        +--> deterministic ESG analysis
        +--> confidence and HITL decision
        +--> supplier-specific follow-up questions
        +--> procurement recommendations
        +--> evidence register and ESG Intelligence Brief
```

The success path in LangGraph is:

```text
ingest_document
-> index_document
-> quality_check
-> retrieve_context
-> extract_indicators
-> analysis_layer
-> assess_confidence
-> generate_questions
-> compile_brief
```

If a PDF is not machine-readable or its BRSR section cannot be located, the
workflow returns a minimal failure brief rather than continuing with an
unreliable assessment.

## Reliability-focused design decisions

### 1. Document-scoped retrieval isolation

The application uses a shared ChromaDB collection but tags every chunk with a
UUID `document_id` and source metadata. Retrieval filters on the active
document:

```python
where={"document_id": document_id}
```

This prevents chunks from one supplier filing from leaking into another
assessment.

### 2. Absence is not the same as extraction failure

The pipeline carries two distinct states through to the brief:

| State | Meaning | Effect on analysis |
| --- | --- | --- |
| `not_found` | Extraction completed but no qualifying disclosure was identified in the supplied evidence. | Deterministic disclosure-gap rules may apply. |
| `extraction_error` | Extraction failed because of an API, rate-limit, authentication, connection, timeout, parsing, or validation issue. | The indicator is unassessed and does not create a false ESG gap. |

When any extraction error exists, the workflow forces **LOW** confidence and
sets the **HITL** flag. Essential Principle 6 extraction errors also make the
completeness result unassessed rather than incomplete.

### 3. Bounded chunking for retrieval quality

A real BRSR false negative showed that oversized page-like chunks could exceed
the effective embedding representation window. Oversized chunks are therefore
subdivided into small overlapping token windows while preserving page,
document, and parent-chunk metadata.

This improvement was validated against a real waste-disclosure retrieval
failure.

### 4. Indicator-specific retrieval

Broad semantic queries can underperform on standardized regulatory tables.
The retriever therefore uses indicator-specific queries for fields such as:

- Scope 3 emissions
- total waste generated
- Scope 1 and Scope 2 emissions
- energy consumption
- water consumption

This was added after cross-company validation showed that broad climate and
waste terminology could rank related but incorrect passages above the exact
BRSR disclosure row.

### 5. Evidence grounding

The Evidence Register keeps disclosure state separate from provenance quality.
Evidence excerpts are matched back to retrieved chunks using strict normalized
matching rather than fuzzy semantic matching.

Possible evidence states include:

- `source_matched`
- `citation_only`
- `excerpt_unmatched`
- `not_found`

The system does not fabricate page references or evidence for genuine
`not_found` results.

### 6. Targeted OpenAI rate-limit recovery

Only `RateLimitError` is retried, for a maximum of three total attempts.

The retry policy:

1. reads server-provided retry/reset information when available,
2. respects the longest requested wait,
3. adds a short safety buffer,
4. falls back to exponential backoff only when no server delay exists,
5. returns `extraction_error` after the final failed attempt.

This prevents transient API failures from being misclassified as ESG
disclosure gaps.

## Real-document validation

The workflow has been exercised against multiple real BRSR filings.

### Reliance Industries

Validation confirmed:

- document-scoped retrieval
- correct total-waste retrieval after chunking hardening
- Scope 3 correctly preserved as `not_found`
- high-confidence assessment
- grounded evidence and procurement follow-up

### Birla Corporation Limited

Validation confirmed:

- legal supplier name extracted from the BRSR rather than inferred from the
  filename
- Scope 3 absolute emissions correctly retrieved as **18,09,403.78 tCO2e**
- Scope 3 classified as **Partial** because a usable accounting methodology was
  not identified
- total waste generated correctly retrieved as **31,223.96 MT**
- procurement recommendations and follow-up questions grounded in the detected
  disclosure gaps

### Sundram Fasteners Limited (SFL)

Validation confirmed:

- a third real-company BRSR completed through the Dockerized API path
- the numbered inline Section A format
  `2. Name of the Listed Entity: Sundram Fasteners Limited (SFL)` is handled
  deterministically instead of falling back to the filename
- the metadata regression exposed by this filing is covered by an automated test

These three filings provide contrasting disclosure and document-format cases
and are used as practical regression examples.

## Automated validation

The maintained test suite currently has **58 passing tests and 11 passing
subtests** covering areas
including:

- semantic extraction
- retrieval regressions
- document isolation
- chunk subdivision
- `not_found` vs `extraction_error`
- gap suppression
- Scope 3 state consistency
- confidence and HITL behavior
- rate-limit handling
- evidence grounding
- procurement recommendations
- supplier-name fallback behavior

## Technology

| Layer | Implementation |
| --- | --- |
| Workflow orchestration | LangGraph |
| LLM extraction | OpenAI Responses API with Pydantic validation |
| Retrieval | ChromaDB with `all-MiniLM-L6-v2` sentence-transformer embeddings |
| Document processing | Python and PyMuPDF |
| Service boundary | Python assessment service |
| API | FastAPI with multipart PDF upload |
| Public contract | Explicit nested Pydantic response models; OpenAPI/Swagger validated |
| User interfaces | Streamlit and Gradio |
| Packaging/runtime | Docker on Python 3.12; Uvicorn; CPU-only PyTorch |
| Tests | `pytest` over the maintained regression suite |

## API and Docker quick start

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Returns API process health. |
| `POST /v1/assessments` | Accepts multipart `file` (PDF) and optional `supplier_name`; returns the assessment envelope. |

The public response is an explicit nested Pydantic `AssessmentEnvelope` with an
optional typed `brief` and controlled `error`, and is published through
OpenAPI/Swagger at `/docs`.

Build and run the verified Python 3.12 image:

```bash
docker build -t esg-supplier-intelligence-api:v1 .
docker run --rm -p 8000:8000 -e OPENAI_API_KEY=your-key-here esg-supplier-intelligence-api:v1
```

Then open `http://localhost:8000/docs` or check
`http://localhost:8000/health`. The image installs CPU-only PyTorch and runs
FastAPI with Uvicorn on port 8000. Cloud deployment is not yet complete.

## Repository layout

```text
app/
|-- agent/        # LangGraph state, routing, nodes, evidence, and compiled graph
|-- api/          # FastAPI routes and explicit public response models
|-- extraction/   # PDF parsing, BRSR detection, prompts, and LLM extraction
|-- rag/          # Chunking, embeddings, Chroma indexing, and retrieval
|-- schemas/      # Structured extraction and assessment schemas
|-- services/     # Shared supplier-assessment service boundary
`-- ui/           # Streamlit and Gradio presentation layers

tests/            # Regression, reliability, retrieval, and UI/service tests
```

Streamlit and Gradio call the same assessment service directly; they do not
route through FastAPI or duplicate domain logic.

## Current limitations

- BRSR filings only; other ESG frameworks are intentionally out of scope for V1.
- Principle 6 is assessed in depth; the remaining BRSR principles are not yet
  analyzed at the same level.
- LLM extraction is currently sequential.
- The application is currently a single-assessment portfolio workflow rather
  than a persistent multi-supplier platform.
- Persistence, authentication, and assessment history are deferred beyond V1.
- Cloud deployment and final `v1.0.0` release packaging remain incomplete.
- Some evidence may remain `citation_only` or `excerpt_unmatched` when strict
  provenance matching cannot safely confirm an exact retrieved-source match.

## V1 roadmap

### Completed

1. LangGraph assessment workflow
2. Principle 6 structured extraction
3. RAG and document-scoped retrieval
4. deterministic Scope 3 and ESG analysis
5. reliability and API-failure handling
6. retrieval/chunking hardening
7. evidence grounding and provenance
8. procurement recommendations and supplier-specific questions
9. Streamlit / Gradio presentation
10. three-company real-BRSR validation: Reliance, Birla, and Sundram Fasteners
11. FastAPI health and multipart assessment endpoints
12. explicit nested Pydantic API contract and Swagger/OpenAPI validation
13. Python 3.12 Docker image with CPU-only PyTorch
14. container startup, health check, and real-company end-to-end validation

### Remaining before V1 release

1. maintained regression validation
2. final documentation, demo assets, and release hardening
3. cloud deployment
4. `v1.0.0` release/tag

## Beyond V1

Future versions are expected to focus on:

- persistent multi-supplier assessments
- PostgreSQL / Supabase and assessment history
- pgvector migration if evaluation justifies it
- supplier comparison
- evaluation and observability with tools such as LangSmith and RAGAS
- checkpointing and persistence
- authentication
- MCP exposure of supplier-assessment capabilities
- supplier-response and follow-up workflows
- specialist agent orchestration where it adds clear business value
- broader ESG-framework support only after the BRSR workflow is mature

## Author

**Baibhav Anand** is a communication and marketing professional transitioning
into AI, analytics, and agentic AI engineering.

This project demonstrates applied Python, LangGraph, RAG, structured LLM
extraction, deterministic business rules, evidence-grounded document
intelligence, reliability engineering, and procurement-oriented AI workflow
design.

See `CHANGELOG.md` for milestone history and engineering decisions.
