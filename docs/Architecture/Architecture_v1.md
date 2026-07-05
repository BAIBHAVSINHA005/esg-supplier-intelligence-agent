Yes. Below is a cleaned, GitHub-ready Markdown version of Claude's architecture response. You can save this directly as:

```text
docs/Architecture/Architecture_v1.md
```

---

# Supplier ESG Intelligence Agent

## Architecture v1

**Status:** Approved Architecture (Phase 5)
**Version:** 1.0
**Date:** July 2026

---

# Architecture Principles

The architecture is built around five core design principles:

1. **Framework Agnostic Design**

   * The classification engine imports a framework schema rather than hard-coding framework names.
   * Adding GRI, CSRD, ISSB, or future frameworks should require a database configuration change rather than application code changes.

2. **Shared State Architecture**

   * All workflow state is stored inside the LangGraph `AssessmentState`.
   * Human-in-the-loop (HITL) review functions as another node in the workflow rather than a separate process.

3. **Separation of Assessment and Output**

   * Assessment records are separated from generated briefs.
   * Future engagement workflows can operate independently from the assessment pipeline.

4. **Tool-Based External Integrations**

   * External systems are accessed through tools rather than hard dependencies.
   * MCP serves as the extension layer for future integrations.

5. **Single Infrastructure Dependency**

   * PostgreSQL and pgvector are hosted within Supabase.
   * The MVP avoids maintaining separate database and vector database systems.

---

# MVP Technology Stack

| Layer               | Technology            | Role                                          |
| ------------------- | --------------------- | --------------------------------------------- |
| Frontend            | Streamlit             | PDF upload, brief display, assessment history |
| Backend API         | FastAPI               | File intake, validation, API endpoints        |
| Agent Orchestration | LangGraph             | Multi-step workflow execution                 |
| LLM                 | Claude Sonnet         | Reasoning, extraction, question generation    |
| PDF Parsing         | PyMuPDF (fitz)        | Text extraction and document analysis         |
| Retrieval           | LangChain + LangGraph | Framework knowledge retrieval                 |
| Vector Store        | pgvector (Supabase)   | Embeddings storage                            |
| Database            | Supabase (PostgreSQL) | Suppliers, assessments, briefs, schemas       |
| Authentication      | Supabase Auth         | User authentication                           |
| MCP Layer           | Python MCP SDK        | External integrations                         |
| Deployment          | Railway + Vercel      | Hosting and CI/CD                             |

---

# Component Responsibilities

## LangGraph

LangGraph acts as the orchestration engine.

Responsibilities:

* Execute workflow nodes
* Maintain shared state
* Route conditional workflow paths
* Manage confidence evaluation
* Trigger HITL directives

The workflow operates on a shared:

```python
AssessmentState
```

containing:

* Document text
* Extracted indicators
* Confidence scores
* ESG gaps
* Follow-up questions
* Flags and directives

---

## RAG + pgvector

The retrieval layer performs two distinct functions.

### Framework Knowledge Retrieval

Stores:

* BRSR schema
* Interpretation rules
* Indicator definitions
* ESG guidance

Purpose:

* Avoid relying solely on LLM pretraining
* Ensure assessments use the latest framework definitions

---

### Document Retrieval

Stores:

* Uploaded supplier document chunks

Purpose:

* Semantic search across supplier disclosures
* Retrieval of evidence from narrative sections
* Scope 3 information discovery

---

## MCP Layer

MCP provides the integration boundary.

### MVP Tools

#### fetch_pdf

Retrieves a PDF from a URL.

Example:

```text
User provides URL
↓
MCP fetches PDF
↓
Pipeline processes document
```

---

#### check_extraction_quality

Returns parsing quality metrics.

Example:

```text
Text Coverage
Table Extraction Confidence
Missing Section Detection
```

---

### Future Tools

V2:

* NSE filing lookup
* CDP search

V3:

* Supplier email generation
* Procurement system updates

---

## Supabase / PostgreSQL

Stores all structured application data.

Examples:

* Suppliers
* Assessments
* Generated briefs
* ESG gaps
* Users
* Framework schemas

---

# Framework Agnostic Architecture

Framework support is database-driven.

The extraction pipeline never references:

```python
"BRSR"
```

directly.

Instead:

```text
Assessment
↓
framework_id
↓
framework_schemas table
↓
Schema JSON
↓
Pipeline
```

Adding a framework requires:

1. Insert framework schema
2. Add UI selection option
3. Execute existing workflow

No workflow node modifications required.

---

# High-Level System Architecture

```text
                ┌───────────────┐
                │   Streamlit   │
                │      UI       │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │   FastAPI     │
                │ Backend Layer │
                └───────┬───────┘
                        │
                        ▼
              ┌───────────────────┐
              │     LangGraph     │
              │ Orchestration Hub │
              └───────┬───────────┘
                      │
      ┌───────────────┼────────────────┐
      ▼               ▼                ▼

┌───────────┐   ┌───────────┐   ┌───────────┐
│  PyMuPDF  │   │    RAG    │   │    MCP    │
│ Extraction│   │ Retrieval │   │  Tools    │
└───────────┘   └───────────┘   └───────────┘
                      │
                      ▼

            ┌────────────────────┐
            │ Supabase/Postgres  │
            │     + pgvector     │
            └────────────────────┘
```

---

# Data Flow

```text
Upload PDF
      │
      ▼
Document Parsing
      │
      ▼
Quality Check
      │
      ├── Low Confidence
      │      │
      │      ▼
      │   HITL Flag
      │
      ▼
Indicator Extraction
      │
      ▼
Analysis
      │
      ▼
Question Generation
      │
      ▼
Brief Compilation
      │
      ▼
Final Output
```

Low-confidence assessments continue through the pipeline but carry a review directive.

---

# LangGraph Workflow

## Node 1 — ingest_document

Responsibilities:

* Parse PDF
* Extract text
* Detect sections
* Generate metadata

Output:

```text
Document Text
Section Map
Document Metadata
```

---

## Node 2 — quality_check

Responsibilities:

* Validate extraction quality
* Detect failures
* Assign confidence level

Possible outcomes:

```text
HIGH
MEDIUM
LOW
FAILURE
```

---

## Node 3 — extract_indicators

Responsibilities:

* Extract BRSR indicators
* Retrieve framework guidance
* Populate structured ESG data

---

## Node 4 — analysis_layer

Responsibilities:

* Disclosure completeness
* Gap detection
* Scope 3 readiness classification

---

## Node 5 — assess_confidence

Responsibilities:

* Review extraction confidence
* Determine HITL requirement

Rule:

```text
LOW Confidence
↓
Set HITL Directive
↓
Continue Pipeline
```

---

## Node 6 — generate_questions

Responsibilities:

* Generate follow-up supplier questions
* Clarify missing disclosures

---

## Node 7 — compile_brief

Responsibilities:

* Build final assessment brief
* Include citations
* Include confidence directives

---

## Conditional Routing Logic

### Quality Check

```text
Document Failure
↓
END
```

Otherwise:

```text
Continue Pipeline
```

---

### Confidence Assessment

```text
LOW Confidence
↓
Set HITL Flag
↓
Continue
```

---

# Human-in-the-Loop (HITL)

## MVP Implementation

HITL is advisory only.

Output:

```text
⚠ Analyst Review Recommended
```

The assessment still completes.

---

## Future Implementation

Workflow becomes:

```text
Low Confidence
↓
Review Queue
↓
Analyst Approval
↓
Final Brief
```

---

# MCP Design Guidelines

Use MCP only when crossing a process or network boundary.

Good MCP Use Cases:

* PDF retrieval from URL
* NSE lookup
* CDP lookup
* Procurement integrations

Avoid MCP for:

* Local PDF parsing
* Local classification logic
* Internal Python functions

These should remain direct function calls.

---

# Implementation Build Order

## Week 1 — Document Pipeline

Build:

* PyMuPDF ingestion
* Section detection
* Text extraction
* Confidence scoring

Success Criteria:

```text
Given a BRSR PDF,
the system extracts Scope 3 content
or produces a Low Confidence flag.
```

---

## Week 2 — Extraction and Classification

Build:

* Indicator schema
* RAG setup
* Classification logic
* Extraction node

Success Criteria:

```text
Classifier passes
10 manually validated test cases.
```

---

## Week 3 — Analysis and API

Build:

* Analysis layer
* Question generation
* Brief generation
* FastAPI endpoints
* Database persistence

Success Criteria:

```text
PDF Upload
↓
Assessment
↓
Structured ESG Brief
```

within 90 seconds.

---

## Week 4 — Frontend and Validation

Build:

* Streamlit UI
* Confidence display
* HITL indicators
* Edge-case handling

Test against:

* Scanned PDFs
* Missing disclosures
* Empty Scope 3 sections

Success Criteria:

All PRD acceptance criteria pass.

---

# Future Roadmap

## Version 2

* Multi-framework support
* Review queue
* NSE integration
* CDP integration

---

## Version 3

* Supplier engagement workflows
* Automated communications
* Procurement system integrations
* Multi-agent workflows

---

# Architecture Status

**Phase 5: Architecture — COMPLETE**

Next Phase:

```text
Phase 6: Implementation Planning
```

Deliverable:

```text
Implementation_Roadmap_v1.md
```

---

This is clean enough to commit directly as `docs/Architecture/Architecture_v1.md` and push to GitHub.
