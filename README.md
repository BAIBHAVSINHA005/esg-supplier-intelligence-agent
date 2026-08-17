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
- regression tests for retrieval, state consistency, grounding, and failure paths

The remaining V1 delivery work is focused on **FastAPI, OpenAPI/Swagger,
Docker, final validation, and release documentation**.

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
Streamlit / Gradio
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

These two filings provide contrasting Scope 3 cases and are used as practical
regression examples.

## Automated validation

The maintained test suite currently has **47 passing tests** covering areas
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
| User interfaces | Streamlit and Gradio |
| Tests | Python `unittest` |
| Planned V1 delivery layer | FastAPI, OpenAPI/Swagger, Docker |

## Repository layout

```text
app/
|-- agent/        # LangGraph state, routing, nodes, evidence, and compiled graph
|-- extraction/   # PDF parsing, BRSR detection, prompts, and LLM extraction
|-- rag/          # Chunking, embeddings, Chroma indexing, and retrieval
|-- schemas/      # Structured extraction and assessment schemas
|-- services/     # Shared supplier-assessment service boundary
`-- ui/           # Streamlit and Gradio presentation layers

tests/            # Regression, reliability, retrieval, and UI/service tests
```

## Current limitations

- BRSR filings only; other ESG frameworks are intentionally out of scope for V1.
- Principle 6 is assessed in depth; the remaining BRSR principles are not yet
  analyzed at the same level.
- LLM extraction is currently sequential.
- The application is currently a single-assessment portfolio workflow rather
  than a persistent multi-supplier platform.
- Persistence, authentication, and assessment history are deferred beyond V1.
- FastAPI and Docker are the remaining V1 delivery-layer milestones.
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
10. multi-company real-BRSR validation

### Remaining before V1 release

1. FastAPI service/API boundary
2. explicit Pydantic request/response contracts
3. OpenAPI/Swagger validation
4. Docker containerization
5. one additional real-company validation
6. final README/demo screenshots and architecture documentation
7. V1 release/tag

## Beyond V1

Future versions are expected to focus on:

- persistent multi-supplier assessments
- PostgreSQL / Supabase and assessment history
- evaluation and observability with tools such as LangSmith and RAGAS
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
