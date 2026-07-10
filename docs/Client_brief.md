# Supplier ESG Intelligence Agent

## Client Brief

---

## Project Summary

The Supplier ESG Intelligence Agent is an AI-powered document intelligence system that transforms a supplier's Business Responsibility and Sustainability Report (BRSR) into a structured ESG Intelligence Brief within 90 seconds.

The system is designed to help ESG analysts and procurement teams rapidly assess supplier ESG disclosures, identify material gaps, evaluate Scope 3 readiness, and generate supplier follow-up questions without manually reviewing hundreds of pages of annual reports.

This project is being developed as a portfolio-grade AI application demonstrating document intelligence, Retrieval-Augmented Generation (RAG), agent orchestration, and ESG domain expertise.

---

## Business Problem

Large organizations increasingly require ESG assessments of suppliers to support:

- BRSR value-chain disclosures
- Scope 3 emissions reporting
- Supplier onboarding
- Procurement risk assessment
- Sustainability compliance requirements

Currently, ESG analysts spend 45–90 minutes reviewing a single supplier filing.

The process typically involves:

1. Locating the supplier annual report
2. Finding the BRSR section
3. Extracting ESG indicators
4. Assessing disclosure quality
5. Identifying missing information
6. Drafting follow-up questions
7. Creating an internal assessment report

This process is slow, inconsistent, and difficult to scale.

---

## Proposed Solution

The Supplier ESG Intelligence Agent automates the initial assessment process.

A user uploads a supplier BRSR PDF, and the system:

1. Extracts and validates document content
2. Locates the BRSR section
3. Extracts ESG indicators
4. Assesses disclosure completeness
5. Classifies Scope 3 readiness
6. Identifies disclosure gaps
7. Generates supplier follow-up questions
8. Produces a structured ESG Intelligence Brief

All findings are supported by document citations to improve transparency and auditability.

---

## Primary Users

### ESG Analyst

**Needs:**

- Faster supplier assessments
- Consistent evaluation methodology
- Source-backed findings
- Ready-to-use supplier questions

### Procurement Manager

**Needs:**

- Simple supplier ESG summaries
- Key disclosure gaps
- Actionable recommendations

---

## Core Features (MVP)

### Document Ingestion

- Upload BRSR PDF
- Extract machine-readable text
- Detect document quality issues

### ESG Extraction

- Extract BRSR indicators
- Capture evidence and citations

### Scope 3 Readiness Assessment

Classification levels:

- Not Found
- Materiality Claim
- Claim Only
- Partial
- Scope 3 Ready

### Disclosure Completeness Assessment

- Assess disclosures across all 9 BRSR Principles
- Highlight missing or incomplete indicators

### Gap Detection

- Identify the most material disclosure gaps
- Prioritize findings for supplier engagement

### Follow-Up Question Generation

- Generate supplier-facing questions
- Support ESG analyst workflows

### ESG Intelligence Brief

- Compile all findings into a structured report
- Present evidence, gaps, and recommendations

---

## Technology Stack

### AI & Agent Framework

- LangGraph
- LangChain

### LLM

- OpenAI GPT Models
- Claude (future option)

### Document Processing

- PyMuPDF

### Vector Database

- ChromaDB

### Frontend

- Streamlit

### Programming Language

- Python

---

## MVP Workflow

```text
Upload PDF
      ↓
Document Ingestion
      ↓
Quality Check
      ↓
Indicator Extraction
      ↓
Analysis Layer
      ↓
Confidence Assessment
      ↓
Question Generation
      ↓
Brief Compilation
      ↓
Final ESG Intelligence Brief
```

---

## Portfolio Learning Objectives

This project demonstrates practical experience in:

### Agent Engineering

- LangGraph state management
- Conditional routing
- Multi-step workflows

### Retrieval-Augmented Generation (RAG)

- ChromaDB integration
- Knowledge-grounded extraction

### Document AI

- PDF ingestion
- Chunking strategies
- Metadata extraction

### Product Thinking

- PRD-driven development
- Architecture-first design
- Enterprise workflow modeling

---

## Success Criteria

The MVP will be considered successful when:

- A BRSR PDF can be processed end-to-end
- A structured ESG Intelligence Brief is generated
- Findings contain source citations
- Scope 3 classification follows defined rules
- Processing completes within approximately 90 seconds
- The application can be demonstrated locally through Streamlit

---

## Current Development Status

### Completed

- Project Charter
- Product Requirements Document (PRD)
- Solution Architecture
- Implementation Roadmap
- LangGraph Foundation Learning

### Current Focus

- LangGraph state design
- AssessmentState implementation
- Transition from learning workflows to production architecture

---

## Project Goal

Build a portfolio-quality AI application that demonstrates:

- Agent-based workflow orchestration
- ESG document intelligence
- Retrieval-Augmented Generation (RAG)
- Enterprise product design
- Applied Generative AI engineering

while solving a realistic sustainability and procurement use case.

---