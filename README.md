# Supplier ESG Intelligence Agent

An evidence-grounded AI workflow that turns a supplier's Indian Business
Responsibility and Sustainability Report (BRSR) into a procurement-ready ESG
Intelligence Brief.

Built as a portfolio project for applied AI and document-intelligence work, it
combines RAG, structured LLM extraction, deterministic ESG rules, and explicit
reliability controls. The aim is not to replace analyst judgement; it is to
give procurement teams a faster, traceable starting point for Scope 3 reporting
and supplier ESG due diligence.

## Why it matters

Supplier sustainability filings contain decision-relevant information, but it
is often buried in long PDFs and reported inconsistently. A buyer needs more
than a text summary: it needs evidence, a clear distinction between a missing
disclosure and a failed extraction, and follow-up questions that can be sent to
the supplier.

This project produces a structured brief containing:

- Scope 3 readiness verdict and supporting evidence
- Principle 6 completeness assessment
- Deterministically identified ESG disclosure gaps
- Recommended procurement actions and supplier follow-up questions
- Confidence level and a human-in-the-loop (HITL) flag

## Current assessment scope

The current release accepts machine-readable BRSR PDFs and assesses
**BRSR Principle 6: Environment**. It covers nine indicators:

| Area | Indicators |
| --- | --- |
| Energy and emissions | Total energy consumption; Scope 1 and Scope 2 GHG emissions; GHG accounting methodology; GHG emissions intensity |
| Value-chain climate data | Scope 3 GHG emissions (leadership indicator); climate or emissions-reduction target |
| Resources and waste | Water consumption; total waste generated |

The intended use cases are supplier onboarding, procurement risk assessment,
Scope 3 data collection, and ESG due diligence.

## How it works

```text
Streamlit UI
  -> supplier assessment service
  -> compiled LangGraph workflow
       -> PDF ingestion and page-level chunking
       -> Chroma indexing
       -> document quality and BRSR checks
       -> document-scoped semantic retrieval
       -> LLM indicator extraction
       -> deterministic ESG analysis
       -> confidence and HITL decision
       -> supplier questions
       -> compiled ESG Intelligence Brief
```

The success path in LangGraph is:

```text
ingest_document -> index_document -> quality_check -> retrieve_context
-> extract_indicators -> analysis_layer -> assess_confidence
-> generate_questions -> compile_brief
```

If a PDF is not machine-readable or its BRSR section cannot be located, the
workflow returns a minimal failure brief rather than continuing with an
unreliable assessment.

## Design decisions that make the workflow reliable

### 1. Document-scoped retrieval isolation

The application uses a single ChromaDB collection, `esg_document_chunks`, but
tags each chunk with a UUID `document_id` and its source page. Retrieval filters
on the active document:

```python
where={"document_id": document_id}
```

This prevents chunks from one supplier filing being retrieved for another.
`document_id` belongs only to the retrieval subsystem; `assessment_id` remains
the separate business-workflow identifier.

### 2. Absence is not the same as an extraction failure

The pipeline carries two distinct states through to the brief:

| State | Meaning | Effect on analysis |
| --- | --- | --- |
| `not_found` | The model completed its assessment of the retrieved evidence and did not identify the disclosure. | Existing deterministic gap rules may apply. |
| `extraction_error` | Extraction failed because of an API, rate-limit, authentication, connection, timeout, parsing, or validation issue. | The indicator is unassessed, is not treated as absent, and does not create a false ESG gap. |

When any extraction error exists, the workflow forces **LOW** confidence and
sets the **HITL** flag. The brief and Streamlit UI explicitly warn that affected
indicators were not assessed. Essential Principle 6 extraction errors also make
the completeness result unassessed rather than incomplete.

### 3. Targeted OpenAI rate-limit recovery

Only `RateLimitError` is retried, for a maximum of three total attempts. The
implementation disables SDK automatic retries so this is the only retry policy.

1. Read `Retry-After` and rate-limit reset headers.
2. Extract a requested wait time from the exception message when needed.
3. Use the longest server-provided delay plus a one-second safety buffer.
4. Fall back to exponential backoff only when no server delay is available.
5. Return `extraction_error` after the final failed attempt.

This avoids retrying earlier than the API instructs and prevents a transient API
failure from being misclassified as an ESG disclosure gap.

## Validation

- **10 automated tests passing**: semantic extraction, extraction-error
  propagation, gap suppression, confidence/HITL behavior, and rate-limit retry
  handling.
- **Reliance BRSR end-to-end validation completed**: document-scoped retrieval
  and Principle 6 structured extraction were verified in a full workflow run.

## Technology

| Layer | Implementation |
| --- | --- |
| Workflow orchestration | LangGraph |
| LLM extraction | OpenAI Responses API with Pydantic validation |
| Retrieval | ChromaDB with `all-MiniLM-L6-v2` sentence-transformer embeddings |
| Document processing | Python and PyMuPDF |
| User interface | Streamlit |
| Tests | Python `unittest` |

## Repository layout

```text
app/
|-- agent/        # LangGraph state, routing, nodes, and compiled graph
|-- extraction/   # PDF parsing, BRSR detection, prompts, and LLM extraction
|-- rag/          # Chunking, embeddings, Chroma indexing, and retrieval
|-- schemas/      # BRSR indicator schema
|-- services/     # Assessment service boundary
`-- ui/           # Streamlit presentation layer

tests/            # Regression and reliability tests
```

## Current limitations

- BRSR filings only; other ESG reporting frameworks are not yet supported.
- Principle 6 only; the remaining BRSR principles are out of scope today.
- LLM indicator extraction is sequential.
- Large reports remain sensitive to OpenAI tokens-per-minute limits, although
  targeted rate-limit recovery is in place.
- Persistence and API deployment have not yet been implemented.

## Roadmap

1. Improve brief narrative quality.
2. Validate the workflow across three supplier filings.
3. Polish the Streamlit experience.
4. Add a FastAPI service layer.
5. Containerize with Docker.
6. Add persistence.

## Author

**Baibhav Anand** is a communication and marketing professional transitioning
into AI, analytics, and agentic AI engineering. This project demonstrates
applied Python, LangGraph, RAG, structured LLM extraction, deterministic rules,
and reliability-focused document intelligence design.

See `CHANGELOG.md` for milestone history and engineering decisions.
