# ESG Supplier Intelligence Agent

AI-powered ESG document intelligence system built with Python, LangGraph, and Generative AI workflows.

## Overview

Organizations increasingly rely on supplier ESG disclosures to assess sustainability risks, procurement decisions, and regulatory readiness. Reviewing lengthy Business Responsibility and Sustainability Reports (BRSRs) manually is time-consuming and difficult to scale.

The ESG Supplier Intelligence Agent automates ESG document analysis by extracting sustainability indicators, identifying disclosure gaps, generating follow-up questions, and producing structured supplier intelligence briefs.

---

## Key Features

### Document Processing
- PDF Ingestion
- BRSR Section Detection
- Principle 6 (Environment) Identification
- Document Quality Assessment

### ESG Analysis
- ESG Indicator Extraction
- Scope 3 Disclosure Assessment
- Gap Analysis
- Confidence Scoring

### Intelligence Generation
- Follow-up Question Generation
- ESG Supplier Intelligence Brief Creation
- Human-in-the-Loop Review Support

### User Experience
- Gradio-based Interface
- End-to-End Workflow Execution

---

## Current Architecture (MVP-1)

```text
START
  ↓
ingest_document
  ↓
quality_check
  ↓
route_after_quality_check
  ├── handle_failure → END
  └── extract_indicators
          ↓
      analysis_layer
          ↓
      assess_confidence
          ↓
      generate_questions
          ↓
      compile_brief
          ↓
         END
```

---

## Tech Stack

- Python
- LangGraph
- Gradio
- PDF Processing
- ESG Analysis Framework
- Rule-Based Extraction Engine

---

## Current Status

### MVP-1 Complete

Implemented:

- PDF ingestion pipeline
- BRSR section detection
- ESG extraction workflow
- Gap analysis engine
- Confidence assessment
- Follow-up question generation
- Gradio user interface
- LangGraph workflow orchestration

---

## MVP-2 Roadmap

Planned enhancements:

- ChromaDB Integration
- Embedding-Based Retrieval
- Retrieval-Augmented Generation (RAG)
- Evidence Grounding
- Enhanced ESG Intelligence
- Improved Disclosure Accuracy

---

## Repository Structure

```text
app/
├── agent/
├── extraction/
├── schemas/
├── ui/

docs/
research/
sandbox/
tests/
```

---

## Author

**Baibhav Anand**

Building AI applications using Python, LangGraph, RAG, MCP, and Agentic AI workflows.

Areas of Interest:

- Generative AI
- Agentic AI
- LangGraph
- RAG Systems
- Business Intelligence
- ESG Intelligence# esg-supplier-intelligence-agent
AI-powered ESG supplier research and disclosure intelligence agent built with LangGraph.
