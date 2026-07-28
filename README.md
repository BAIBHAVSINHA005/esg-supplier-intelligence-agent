# Supplier ESG Intelligence Agent

An AI-powered document intelligence system that transforms a supplier's **Business Responsibility and Sustainability Report (BRSR)** into a structured **ESG Intelligence Brief** in under 90 seconds.

The project combines **LangGraph**, **Retrieval-Augmented Generation (RAG)**, **LLM-based information extraction**, and **deterministic ESG analysis** to automate supplier sustainability assessments.

---

# Business Problem

Organizations increasingly require ESG assessments of suppliers to support:

- Scope 3 emissions reporting
- Supplier onboarding
- Procurement risk assessment
- ESG due diligence
- Sustainability compliance

Today, ESG analysts often spend **45–90 minutes** manually reviewing a single supplier's sustainability report.

This project automates that workflow by extracting ESG disclosures, evaluating disclosure completeness, identifying reporting gaps, and generating an evidence-backed ESG Intelligence Brief within minutes.

---

# Solution

The Supplier ESG Intelligence Agent performs an end-to-end ESG document analysis pipeline.

## Workflow

1. Upload a supplier BRSR PDF
2. Assess document quality
3. Detect the reporting framework
4. Index the document into a vector database
5. Retrieve relevant evidence using RAG
6. Extract ESG indicators using an LLM
7. Perform deterministic ESG analysis
8. Detect disclosure gaps
9. Assess Scope 3 reporting readiness
10. Generate supplier follow-up questions
11. Produce a structured ESG Intelligence Brief

All findings are traceable to supporting evidence retrieved from the source document.

---

# Current Architecture (v0.3.1)

```text
                    Supplier BRSR PDF
                           │
                           ▼
                    PDF Processing
                           │
                           ▼
                 Quality Assessment
                           │
                           ▼
               ChromaDB Vector Index
                           │
                           ▼
                Retrieval (RAG Pipeline)
                           │
                           ▼
                 LLM ESG Extraction
                           │
                           ▼
             Deterministic ESG Analysis
                           │
                           ▼
              ESG Intelligence Brief
```

---

# Current Status

**Latest Release:** **v0.3.1**

### Completed Features

- ✅ PDF ingestion
- ✅ Document quality assessment
- ✅ BRSR framework detection
- ✅ PDF chunking
- ✅ ChromaDB vector database
- ✅ Retrieval-Augmented Generation (RAG)
- ✅ OpenAI embedding-based retrieval
- ✅ LLM-driven ESG indicator extraction
- ✅ Semantic metadata extraction
- ✅ Deterministic ESG analysis
- ✅ Gap detection
- ✅ Scope 3 readiness assessment
- ✅ Supplier follow-up question generation
- ✅ Structured ESG Intelligence Brief generation
- ✅ Gradio web interface
- ✅ LangGraph workflow orchestration
- ✅ Regression tests for semantic extraction

---

# Key Features

- Retrieval-Augmented Generation (RAG)
- Evidence-backed ESG extraction
- Semantic metadata extraction
- Structured ESG indicator mapping
- Deterministic post-processing
- Disclosure gap analysis
- Scope 3 readiness assessment
- Supplier intelligence report generation
- Interactive Gradio interface

---

# Tech Stack

## AI & LLM

- OpenAI GPT
- LangChain
- LangGraph

## Retrieval

- ChromaDB
- OpenAI Embeddings

## Backend

- Python
- Pydantic
- PyMuPDF

## User Interface

- Gradio

## Testing

- Pytest

---

# Project Structure

```text
app/
│
├── ingestion/
├── retrieval/
├── extraction/
├── analysis/
├── ui/
├── schemas/
└── workflow/

tests/

docs/

data/

research/

README.md
CHANGELOG.md
requirements.txt
```

---

# Technical Highlights

This project demonstrates practical implementation of modern AI engineering concepts.

### Agent Engineering

- LangGraph state management
- Multi-stage AI workflows
- Conditional routing
- Modular pipeline architecture

### Retrieval-Augmented Generation

- Document chunking
- Embedding generation
- Vector search
- Context-aware retrieval

### Document AI

- PDF parsing
- ESG information extraction
- Evidence grounding
- Structured data generation

### Software Engineering

- PRD-driven development
- Modular architecture
- Regression testing
- Versioned releases
- Git-based milestone tracking

---

# Next Milestone

## MVP 3.1.5

Planned improvements:

- Document-scoped retrieval
- Metadata-based filtering
- Improved retrieval precision
- Eliminate cross-document retrieval contamination
- Enhanced retrieval evaluation

---

# Screenshots

*(To be added)*

- Upload Interface
- ESG Intelligence Brief
- Workflow Visualization

---

# Release History

See **CHANGELOG.md** for:

- Version history
- Development milestones
- Bug fixes
- Engineering decisions
- Planned improvements

---

# Author

**Baibhav Anand**

Communication and Marketing professional transitioning into AI, Analytics, and Agentic AI Engineering.

Currently building enterprise AI applications using:

- Python
- LangGraph
- Retrieval-Augmented Generation (RAG)
- Model Context Protocol (MCP)
- Agentic AI workflows

GitHub portfolio showcasing AI, analytics, and intelligent document processing projects.