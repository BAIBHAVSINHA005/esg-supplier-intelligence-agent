# Supplier ESG Intelligence Agent

## Client Brief

---

## Project Summary

The Supplier ESG Intelligence Agent is an evidence-grounded AI document intelligence system that converts an Indian supplier's Business Responsibility and Sustainability Report (BRSR) into a procurement-ready ESG Intelligence Brief.

The current V1 focuses on **BRSR Principle 6: Environment** and helps sustainability and procurement teams determine whether a supplier's disclosed ESG information is sufficiently complete, traceable, and usable for:

- Scope 3 data collection
- supplier due diligence
- procurement follow-up
- disclosure-gap identification
- evidence-backed ESG review

The system is designed to accelerate the initial analyst review while keeping source evidence, confidence, and human review requirements visible.

---

## Business Problem

Supplier sustainability filings contain important procurement and climate data, but that information is often:

- buried in long PDF reports
- split across tables and narrative sections
- reported inconsistently between companies
- difficult to compare manually
- incomplete for Scope 3 decision use

A procurement or ESG analyst therefore needs more than a summary.

The practical questions are:

- Is the disclosure actually present?
- Is the extracted value traceable to the source?
- Is Scope 3 information usable or only partially disclosed?
- Which data gaps matter to the buyer?
- What should the supplier be asked next?

Manual review is difficult to scale across a large supplier base.

---

## Proposed Solution

A user uploads a machine-readable supplier BRSR PDF.

The system then:

1. extracts and validates the document
2. identifies relevant BRSR content
3. indexes document chunks for retrieval
4. retrieves evidence separately for each target ESG indicator
5. performs structured LLM extraction
6. applies deterministic ESG and Scope 3 rules
7. assesses confidence and HITL requirements
8. creates an evidence register
9. identifies procurement-relevant disclosure gaps
10. generates supplier-specific follow-up questions
11. produces deterministic procurement recommendations
12. compiles the final ESG Intelligence Brief

The system is designed to distinguish a **missing disclosure** from a **failed extraction**, reducing the risk of creating false ESG gaps from technical failures.

---

## Primary Users

### Procurement Manager

Needs:
- clear supplier ESG conclusions
- Scope 3 usability assessment
- critical disclosure gaps
- recommended procurement action
- supplier-ready follow-up questions
- evidence that can be reviewed when required

### ESG / Sustainability Analyst

Needs:
- faster first-pass supplier assessment
- structured Principle 6 extraction
- traceable evidence
- consistent Scope 3 classification
- confidence and review flags
- less time spent locating disclosure details manually

### Potential Consulting / Client Use

The V1 can also serve as the foundation for a client-specific supplier ESG assessment workflow where a buyer repeatedly receives sustainability disclosures from vendors and needs a consistent evidence-grounded screening process.

A production deployment would require additional controls such as persistence,
authentication, data governance, and operational monitoring.

---

## Current V1 Assessment Scope

V1 assesses **nine Principle 6 indicators**.

### Energy and emissions
- Total energy consumption
- Scope 1 GHG emissions
- Scope 2 GHG emissions
- GHG accounting methodology
- GHG emissions intensity

### Value-chain climate data
- Scope 3 GHG emissions
- climate or emissions-reduction target

### Resources and waste
- Water consumption
- Total waste generated

V1 deliberately prioritizes depth and reliability in this scope rather than broad but shallow coverage of every ESG framework.

---

## Scope 3 Readiness

The system does not reduce Scope 3 to a yes/no disclosure flag.

Representative classifications include:

- **Not Found**
- **Claim Only**
- **Materiality Claim**
- **Partial**
- **Ready / sufficiently disclosed**

The distinction matters because a supplier may disclose an absolute Scope 3 number but still lack the methodology or supporting context a buyer needs to use that information confidently.

The business question is:

> **Can the buyer actually use this supplier's disclosed Scope 3 information?**

---

## ESG Intelligence Brief

The final output is structured around procurement decision use.

### Executive Summary
A concise supplier-level conclusion.

### Scope 3 Assessment
A graded readiness verdict with an explanation of why the disclosure is or is not usable.

### Principle 6 Completeness
A structured view of assessed environmental disclosures.

### Critical Gaps
Deterministically identified missing or insufficient disclosures.

### Supplier Follow-Up Questions
Questions linked to the specific gaps found in the supplier's filing.

### Procurement Recommendations
Recommended actions derived from existing gaps and findings rather than newly invented model claims.

### Confidence / HITL
A reliability signal showing whether analyst review is recommended.

### Evidence Details
Expandable provenance showing the source support available for extracted findings.

---

## Reliability Controls

### Document Isolation

Each assessment uses a unique `document_id` and retrieval is filtered to the active supplier document.

This prevents evidence from one filing from being retrieved during another supplier assessment.

### Missing vs Failed Extraction

The system preserves two different states:

- `not_found` — no qualifying disclosure identified
- `extraction_error` — the indicator could not be assessed reliably because of a technical or validation failure

An extraction failure does not automatically create an ESG gap.

### Evidence Grounding

Evidence is matched back to retrieved document chunks using strict normalized matching.

The system prefers incomplete provenance over invented provenance.

### Rate-Limit Handling

OpenAI rate-limit failures use bounded retry behavior and become `extraction_error` after the final failed attempt.

---

## Real-Document Validation

### Reliance Industries

The workflow was validated against a real Reliance BRSR.

Important outcomes included:
- correct recovery of Total Waste Generated after retrieval hardening
- Scope 3 correctly retained as `not_found`
- HIGH confidence
- grounded procurement output

### Birla Corporation Limited

A second-company validation tested generalization.

Validated outcomes included:
- supplier legal name resolved from the filing
- Scope 3 emissions retrieved as `18,09,403.78 tCO2e`
- Scope 3 classified as Partial
- Total Waste Generated retrieved as `31,223.96 MT`
- supplier questions and recommendations grounded in current findings

These two filings exposed different retrieval and disclosure patterns and were used to strengthen the pipeline.

---

## Current Technology

### Workflow
- LangGraph

### LLM / Structured Extraction
- OpenAI Responses API
- Pydantic validation

### Retrieval
- ChromaDB
- `all-MiniLM-L6-v2` sentence-transformer embeddings

### Document Processing
- PyMuPDF

### Application Layer
- Python supplier-assessment service
- FastAPI
- explicit nested Pydantic public response contract
- OpenAPI / Swagger

### User Interfaces
- Streamlit
- Gradio

### Testing
- maintained `pytest` regression suite

### Packaging and Runtime
- Docker on Python 3.12
- CPU-only PyTorch
- Uvicorn serving FastAPI inside the container

---

## Current Validation Baseline

**57 automated tests and 11 subtests passing; 0 failures**

Coverage includes:
- retrieval regressions
- document isolation
- chunk subdivision
- extraction failure handling
- Scope 3 state consistency
- confidence / HITL
- evidence grounding
- procurement recommendations
- supplier-name handling

---

## What V1 Does Not Yet Include

The following are intentionally outside the current V1:

- persistence and assessment history
- authentication
- multi-user access
- Supabase / PostgreSQL
- pgvector
- multi-supplier comparison
- supplier email automation
- procurement-system integrations
- MCP
- autonomous multi-agent workflows
- GRI / CSRD / ISSB / CDP support

These are possible later product capabilities rather than hidden dependencies of the current workflow.

---

## Business Value

The V1 demonstrates how an AI-assisted supplier ESG review can move from:

```text
long sustainability filing
    ->
structured evidence
    ->
Scope 3 usability assessment
    ->
identified information gaps
    ->
supplier questions
    ->
procurement action
```

The value is not simply document summarization.

The product is intended to turn supplier sustainability disclosures into **traceable, procurement-ready Scope 3 intelligence**.

---

## Current Development Status

### Completed
- core LangGraph workflow
- BRSR ingestion
- document-scoped RAG
- indicator-specific retrieval
- structured extraction
- deterministic ESG analysis
- Scope 3 readiness classification
- confidence / HITL
- evidence grounding
- procurement recommendations
- supplier-specific questions
- Streamlit / Gradio presentation
- Reliance and Birla validation
- FastAPI health and multipart assessment endpoints
- explicit API response contracts and Swagger/OpenAPI validation
- Docker build, startup, and health validation
- real Birla BRSR assessment completed end-to-end inside Docker with HTTP 200

### Remaining Before V1 Release
- maintained regression validation
- final documentation, demo assets, and release hardening
- third weaker-BRSR validation if retained
- cloud deployment
- `v1.0.0` release/tag

---

## Product Direction

### V2
Persistent multi-supplier assessment and supplier-response workflows.

Potential capabilities:
- PostgreSQL / Supabase
- assessment history
- supplier comparison
- evaluation / observability
- checkpointing / persistence
- MCP
- authentication where justified

### V3
Controlled specialist-agent workflows for:
- disclosure discovery
- evidence verification
- supplier engagement
- procurement support

### V4
Enterprise supplier portfolio intelligence:
- multi-year supplier history
- benchmarking
- cross-framework mappings
- broader supplier data relationships

---

## Project Positioning

This project is suitable as:

- an applied AI / GenAI engineering portfolio project
- a technical case study for AI Solutions or Agentic AI roles
- a prototype for supplier ESG / Scope 3 consulting
- a foundation for a client-specific procurement intelligence workflow

It demonstrates that the AI layer, the ESG rules, the evidence model, and the procurement workflow can be designed together rather than as separate demo components.
