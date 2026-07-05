# Supplier ESG Intelligence Agent
# Implementation Roadmap v1

**Role:** Senior AI Engineer / Technical Lead
**Audience:** Solo developer — intermediate Python, learning LangGraph
**Goal:** Portfolio-quality MVP demonstrating LangGraph, RAG, PDF processing, and ESG analysis
**Timeline:** 4 weeks

---

## Table of Contents

1. [MVP Scope Definition](#1-mvp-scope-definition)
2. [Development Phases](#2-development-phases)
3. [Folder Structure](#3-folder-structure)
4. [LangGraph Design](#4-langgraph-design)
5. [MVP Node Specifications](#5-mvp-node-specifications)
6. [Technical Learning Dependencies](#6-technical-learning-dependencies)
7. [Weekly Build Plan](#7-weekly-build-plan)
8. [First Coding Task](#8-first-coding-task)
9. [Acceptance Criteria](#9-acceptance-criteria)

---

## 1. MVP Scope Definition

### What is built in V1

| Feature | Description |
|---|---|
| PDF ingestion | Accept a single BRSR PDF upload via Streamlit |
| Document quality check | Assess machine readability, locate BRSR section, score extraction confidence |
| Structured extraction | Extract ESG indicator data against the BRSR indicator schema |
| Scope 3 readiness classification | Apply the four-level Scope 3 verdict using the decision tree from the PRD |
| Disclosure completeness assessment | Score all 9 BRSR principles as Complete / Partial / Not Found |
| Gap detection | Identify and rank the top 5 disclosure gaps with citations |
| Follow-up question generation | Generate 3–5 supplier-facing questions from detected gaps |
| Confidence indicator | Produce a High / Medium / Low confidence rating with a behavioural directive |
| Brief compilation | Assemble a structured ESG Intelligence Brief with source citations |
| Streamlit UI | Upload page, processing view, brief viewer |
| ChromaDB RAG | Local vector store for BRSR framework knowledge and document chunks |
| JSON persistence | Save completed briefs as local JSON files (no database required) |
| HITL flag | Surface a human review directive in the brief output when confidence is Low |

### What is explicitly excluded from V1

| Excluded Feature | Reason |
|---|---|
| FastAPI backend | Not needed — Streamlit calls LangGraph directly |
| Supabase / PostgreSQL | Postponed — JSON file storage is sufficient for MVP |
| MCP tools | Not required for MVP — direct Python function calls are used instead |
| Authentication / multi-user | Not a portfolio requirement; single-user local tool |
| Multi-supplier comparison | V2 feature — requires persistent storage |
| Annual report ingestion | V2 — MVP accepts BRSR-only PDFs |
| Risk scoring / escalation levels | V2 — requires judgment beyond disclosure analysis |
| Supplier ESG Program Signals | V2 — adds complexity before core loop is validated |
| GRI / CSRD / ISSB mapping | V3 — multi-framework translation |
| Docker / deployment | Portfolio demo runs locally; deployment is a V2 concern |
| Next.js frontend | V2 — Streamlit is sufficient for MVP and portfolio demo |

### V2 Features (after MVP is complete and validated)

- Supabase integration for persistent assessment storage
- Multi-supplier comparison view
- Sector-adjusted gap weighting
- Annual report ingestion with BRSR chapter extraction
- Web search for supplementary supplier data (CDP, sustainability reports)
- Supplier ESG Program Signals section
- Export brief to PDF

### V3 Features (platform phase)

- GRI / ISSB / CSRD framework mapping
- Supplier engagement workflow (draft and track follow-up outreach)
- Risk scoring and escalation recommendations
- MCP tools for NSE filing fetch, email send, procurement system integration
- FastAPI backend with Supabase and multi-user support

---

## 2. Development Phases

### Phase 1 — LangGraph Foundation
**Goal:** Build and run a working LangGraph pipeline with no ESG logic.
Understand state, nodes, edges, conditional routing, and graph invocation before adding domain complexity.

**Deliverable:** A 3-node LangGraph pipeline that accepts text, checks its length, and summarises it using Claude.

---

### Phase 2 — PDF Ingestion
**Goal:** Accept a BRSR PDF, extract clean text, locate the BRSR section, and score extraction confidence.

**Deliverable:** The `ingest_document` and `quality_check` nodes working end-to-end. For any uploaded BRSR PDF, the pipeline outputs: extracted text, a confidence score, a boolean for whether the BRSR section was found, and a document failure flag.

---

### Phase 3 — ESG Extraction
**Goal:** Extract structured indicator data from the BRSR text against the BRSR schema.

**Deliverable:** The `extract_indicators` node working against a hardcoded BRSR indicator checklist (no RAG yet). For a given principle section, the node returns each indicator's state (Disclosed / Partially Disclosed / Not Found) and a source citation.

---

### Phase 4 — RAG Integration
**Goal:** Load the BRSR framework knowledge base into ChromaDB. Replace the hardcoded schema with RAG-retrieved context.

**Deliverable:** ChromaDB running locally with the BRSR knowledge base indexed. The `extract_indicators` node now retrieves indicator definitions and guidance from ChromaDB to ground each extraction decision.

---

### Phase 5 — Streamlit UI
**Goal:** Build the user-facing interface for upload, processing feedback, and brief display.

**Deliverable:** A working Streamlit app where a user can upload a BRSR PDF, see a progress indicator while processing runs, and view the structured brief output with all sections.

---

### Phase 6 — End-to-End MVP
**Goal:** Wire all phases together. Run the complete LangGraph pipeline from upload to brief. Validate against 5 real BRSR filings.

**Deliverable:** A running local MVP that passes all acceptance criteria in Section 9.

---

## 3. Folder Structure

```
supplier-esg-agent/
│
├── README.md                          # Project overview, setup instructions, demo GIF
├── .env                               # API keys — never commit this file
├── .env.example                       # Template for environment variables
├── .gitignore                         # Exclude .env, data/, __pycache__, etc.
├── requirements.txt                   # All Python dependencies
│
├── app/                               # Main application code
│   │
│   ├── main.py                        # Streamlit entry point — run with: streamlit run app/main.py
│   │
│   ├── agent/                         # LangGraph agent — the core of the product
│   │   ├── __init__.py
│   │   ├── state.py                   # AssessmentState TypedDict definition
│   │   ├── graph.py                   # Graph assembly: nodes + edges + compile
│   │   │
│   │   ├── nodes/                     # One file per LangGraph node
│   │   │   ├── __init__.py
│   │   │   ├── ingest.py              # ingest_document: PDF bytes → extracted text + chunks
│   │   │   ├── quality.py             # quality_check: text → confidence score + section detection
│   │   │   ├── extract.py             # extract_indicators: text + schema → indicator states
│   │   │   ├── analysis.py            # analysis_layer: indicators → scope3 + completeness + gaps
│   │   │   ├── confidence.py          # assess_confidence: all outputs → confidence level + directive
│   │   │   ├── questions.py           # generate_questions: gaps → follow-up questions
│   │   │   ├── brief.py               # compile_brief: all state → final structured brief
│   │   │   └── failure.py             # handle_failure: document failure → error brief
│   │   │
│   │   └── edges/
│   │       ├── __init__.py
│   │       └── routing.py             # Conditional routing functions (used in add_conditional_edges)
│   │
│   ├── rag/                           # RAG layer — ChromaDB + embeddings + retrieval
│   │   ├── __init__.py
│   │   ├── client.py                  # ChromaDB client setup (local persistent)
│   │   ├── collections.py             # Collection definitions: framework_knowledge, document_chunks
│   │   ├── embeddings.py              # Embedding model setup (sentence-transformers)
│   │   ├── retriever.py               # Retrieval functions: retrieve_indicator_context(), retrieve_from_doc()
│   │   └── loader.py                  # Load and index knowledge_base/ into ChromaDB on startup
│   │
│   ├── extraction/                    # PDF processing utilities
│   │   ├── __init__.py
│   │   ├── pdf_parser.py              # PyMuPDF: extract text, detect tables, score readability
│   │   ├── section_detector.py        # Locate BRSR section within a larger annual report PDF
│   │   └── table_extractor.py         # Extract table content from BRSR Principle 6
│   │
│   ├── classification/                # ESG classification logic — pure functions, no LLM calls
│   │   ├── __init__.py
│   │   ├── scope3_classifier.py       # Scope 3 decision tree: text + indicators → level
│   │   ├── completeness.py            # Per-principle completeness scoring
│   │   └── gap_detector.py            # Gap identification and priority ranking
│   │
│   ├── schemas/                       # BRSR framework schemas — structured as JSON/dict
│   │   ├── __init__.py
│   │   ├── brsr_v2023.json            # Complete BRSR indicator checklist (9 principles, 98 essential indicators)
│   │   └── loader.py                  # Load and validate schema files
│   │
│   ├── ui/                            # Streamlit pages and components
│   │   ├── __init__.py
│   │   │
│   │   ├── pages/
│   │   │   ├── upload.py              # Page 1: Upload BRSR PDF + enter supplier name
│   │   │   ├── processing.py          # Page 2: Progress spinner + live status messages
│   │   │   ├── brief_viewer.py        # Page 3: Full structured brief display
│   │   │   └── history.py             # Page 4: List of past assessments (loaded from JSON)
│   │   │
│   │   └── components/
│   │       ├── completeness_table.py  # Render 9-principle completeness table
│   │       ├── scope3_badge.py        # Colour-coded Scope 3 verdict badge
│   │       ├── gap_card.py            # Individual gap display card
│   │       ├── question_card.py       # Follow-up question display
│   │       └── confidence_banner.py   # Top-of-brief confidence directive banner
│   │
│   └── utils/
│       ├── __init__.py
│       ├── citations.py               # Format citation strings from raw extraction metadata
│       ├── storage.py                 # Save/load brief JSON to data/assessments/
│       └── logger.py                  # Configured logger for all modules
│
├── knowledge_base/                    # Your ESG course materials — this is the RAG corpus
│   │
│   ├── brsr/                          # BRSR-specific knowledge
│   │   ├── overview.md                # BRSR background, history, SEBI mandate
│   │   ├── principles/
│   │   │   ├── principle_1_ethics.md
│   │   │   ├── principle_2_products.md
│   │   │   ├── principle_3_employees.md
│   │   │   ├── principle_4_stakeholders.md
│   │   │   ├── principle_5_human_rights.md
│   │   │   ├── principle_6_environment.md  # Most important — Scope 1/2/3 guidance
│   │   │   ├── principle_7_policy.md
│   │   │   ├── principle_8_inclusive.md
│   │   │   └── principle_9_consumer.md
│   │   └── indicators/
│   │       ├── essential_indicators.md    # All 98 essential indicators with descriptions
│   │       └── leadership_indicators.md  # All 42 leadership indicators
│   │
│   └── esg_concepts/                  # Supporting ESG knowledge for RAG context
│       ├── scope3_guidance.md         # GHG Protocol Scope 3 categories, methodology
│       ├── ghg_accounting.md          # GHG Protocol basics, ISO 14064
│       └── brsr_core.md               # BRSR Core KPIs and assurance requirements
│
├── tests/                             # Tests — start small, grow as you build
│   ├── __init__.py
│   ├── fixtures/
│   │   └── sample_brsr_text.txt       # Extracted text from a real BRSR for unit tests
│   ├── test_scope3_classifier.py      # Unit tests for Scope 3 decision tree
│   ├── test_completeness.py           # Unit tests for completeness scoring
│   ├── test_gap_detector.py           # Unit tests for gap detection
│   ├── test_pdf_parser.py             # Unit tests for PDF parsing
│   └── test_graph.py                  # Integration test: run full graph on sample document
│
├── data/                              # Local data storage — excluded from Git
│   ├── chromadb/                      # ChromaDB local persistent storage
│   ├── uploads/                       # Temporary PDF uploads (cleared after processing)
│   └── assessments/                   # Completed brief JSON files
│       └── .gitkeep
│
└── docs/
    ├── Architecture/
    │   └── Architecture_v1.md
    └── Implementation_Roadmap_v1.md   # This document
```

### Key design decisions in this structure

**Why is `classification/` separate from `nodes/`?**
The Scope 3 classifier, completeness assessor, and gap detector are pure functions — they take extracted text and return structured results. They do not call LLMs and do not need LangGraph context. Keeping them in `classification/` means they can be unit-tested in complete isolation, which is essential for validating the PRD's classification rules.

**Why does `agent/nodes/` have one file per node?**
Each LangGraph node has distinct responsibilities and will grow independently. One file per node makes it easy to work on a single step without navigating a large monolithic file.

**Why `knowledge_base/` as markdown files?**
Your ESG course materials become the RAG corpus. Storing them as markdown files means you can edit and extend them without touching code. The `rag/loader.py` script indexes them into ChromaDB on startup.

**Why JSON files instead of a database?**
For an MVP and portfolio demo, JSON files are sufficient. They are human-readable, debuggable, and version-controllable. The storage interface is abstracted into `utils/storage.py`, so swapping to Supabase in V2 is a single file change.

---

## 4. LangGraph Design

### AssessmentState Definition

This is the single most important data structure in the project. All nodes read from and write to this shared state object. It is defined once in `app/agent/state.py` and never duplicated.

```python
# app/agent/state.py

from typing import TypedDict, Optional, Literal, List, Dict, Any


class AssessmentState(TypedDict):
    """
    Shared state object passed between all LangGraph nodes.
    Each node reads the fields it needs and writes back only its own outputs.
    Fields are never deleted — only added or updated.
    """

    # ── INPUT (set by the caller before graph.invoke()) ────────────────────
    assessment_id: str              # UUID generated before invoking the graph
    supplier_name: str              # Company name entered by the user
    source_filename: str            # Original PDF filename
    document_bytes: bytes           # Raw PDF file bytes

    # ── DOCUMENT INGESTION (written by: ingest_document) ───────────────────
    document_text: str              # Full extracted text from PDF
    document_chunks: List[Dict]     # List of {text, page, section, is_table}
    num_pages: int                  # Total pages in the PDF

    # ── QUALITY CHECK (written by: quality_check) ──────────────────────────
    is_machine_readable: bool       # True if text layer is extractable
    brsr_section_found: bool        # True if BRSR chapter was located
    brsr_section_text: str          # Extracted text of the BRSR section only
    extraction_confidence_score: float  # 0.0–1.0 raw score before level assignment
    document_failure: bool          # True if document cannot be processed
    document_failure_reason: Optional[str]

    # ── EXTRACTION (written by: extract_indicators) ─────────────────────────
    extracted_indicators: Dict[str, Any]
    # Structure:
    # {
    #   "principle_6": {
    #     "scope_1_emissions": {
    #       "state": "disclosed",        # disclosed | partially_disclosed | not_found
    #       "value": "12,450 tCO2e",
    #       "citation": "Principle 6, Essential Indicator E-7, Page 142"
    #     },
    #     ...
    #   }
    # }

    # ── ANALYSIS (written by: analysis_layer) ──────────────────────────────
    scope3_verdict: Dict[str, Any]
    # Structure:
    # {
    #   "level": "partial",             # not_found | claim_only | partial | scope3_ready | materiality_claim
    #   "evidence": "Extracted text...",
    #   "citation": "Principle 6, Page 144",
    #   "maturity_signals": {
    #     "assurance": "not_found",
    #     "category_boundary": "not_found",
    #     "sbti": "not_found",
    #     "significant_partners": "not_found",
    #     "trend_data": "not_found"
    #   }
    # }

    completeness_results: List[Dict]
    # Structure: list of 9 items, one per BRSR principle
    # [
    #   {
    #     "principle_number": 6,
    #     "principle_name": "Environment",
    #     "state": "partial",           # complete | partial | not_found
    #     "citation": "Section C, Principle 6, Pages 140–148",
    #     "partial_indicators": ["scope_3_emissions", "water_intensity"]
    #   },
    #   ...
    # ]

    gaps: List[Dict]
    # Structure: list of up to 5 items
    # [
    #   {
    #     "rank": 1,
    #     "gap_id": "G-01",
    #     "gap_name": "Scope 3 not disclosed",
    #     "brsr_reference": "Principle 6, Essential Indicator E-8",
    #     "severity": "critical",
    #     "description": "...",
    #     "citation": "Not found in uploaded BRSR filing — Principle 6, Indicator E-8 checked"
    #   }
    # ]

    # ── CONFIDENCE (written by: assess_confidence) ─────────────────────────
    confidence_level: Literal["high", "medium", "low"]
    confidence_directive: str       # The full behavioural directive text
    hitl_flag: bool                 # True when confidence is Low or medium with uncertain fields
    uncertain_fields: List[str]     # Field names marked [⚠] in the brief

    # ── OUTPUT (written by: generate_questions + compile_brief) ────────────
    followup_questions: List[Dict]
    # Structure:
    # [
    #   {
    #     "rank": 1,
    #     "question": "Your BRSR does not include...",
    #     "linked_gap_id": "G-01"
    #   }
    # ]

    brief: Optional[Dict]           # Final assembled brief — None until compile_brief runs
    error: Optional[str]            # Error message if document_failure is True
```

---

### Node List

| Node | File | Calls Claude? | Calls ChromaDB? |
|---|---|---|---|
| `ingest_document` | `nodes/ingest.py` | No | No |
| `quality_check` | `nodes/quality.py` | No | No |
| `extract_indicators` | `nodes/extract.py` | Yes | Yes |
| `analysis_layer` | `nodes/analysis.py` | Yes | No |
| `assess_confidence` | `nodes/confidence.py` | No | No |
| `generate_questions` | `nodes/questions.py` | Yes | No |
| `compile_brief` | `nodes/brief.py` | No | No |
| `handle_failure` | `nodes/failure.py` | No | No |

---

### Edge List

| From | To | Type | Condition |
|---|---|---|---|
| `START` | `ingest_document` | Always | — |
| `ingest_document` | `quality_check` | Always | — |
| `quality_check` | `extract_indicators` | Conditional | `state["document_failure"] == False` |
| `quality_check` | `handle_failure` | Conditional | `state["document_failure"] == True` |
| `extract_indicators` | `analysis_layer` | Always | — |
| `analysis_layer` | `assess_confidence` | Always | — |
| `assess_confidence` | `generate_questions` | Always | — |
| `generate_questions` | `compile_brief` | Always | — |
| `compile_brief` | `END` | Always | — |
| `handle_failure` | `END` | Always | — |

---

### Conditional Routing Logic

```python
# app/agent/edges/routing.py

from app.agent.state import AssessmentState


def route_after_quality_check(state: AssessmentState) -> str:
    """
    Called by LangGraph after quality_check completes.
    Returns the name of the next node to execute.
    """
    if state.get("document_failure", False):
        return "handle_failure"
    return "extract_indicators"
```

---

### Graph Assembly

```python
# app/agent/graph.py

from langgraph.graph import StateGraph, END

from app.agent.state import AssessmentState
from app.agent.nodes.ingest import ingest_document
from app.agent.nodes.quality import quality_check
from app.agent.nodes.extract import extract_indicators
from app.agent.nodes.analysis import analysis_layer
from app.agent.nodes.confidence import assess_confidence
from app.agent.nodes.questions import generate_questions
from app.agent.nodes.brief import compile_brief
from app.agent.nodes.failure import handle_failure
from app.agent.edges.routing import route_after_quality_check


def build_graph():
    """Build and compile the ESG Intelligence Agent LangGraph graph."""

    workflow = StateGraph(AssessmentState)

    # Register nodes
    workflow.add_node("ingest_document", ingest_document)
    workflow.add_node("quality_check", quality_check)
    workflow.add_node("extract_indicators", extract_indicators)
    workflow.add_node("analysis_layer", analysis_layer)
    workflow.add_node("assess_confidence", assess_confidence)
    workflow.add_node("generate_questions", generate_questions)
    workflow.add_node("compile_brief", compile_brief)
    workflow.add_node("handle_failure", handle_failure)

    # Set entry point
    workflow.set_entry_point("ingest_document")

    # Sequential edges
    workflow.add_edge("ingest_document", "quality_check")
    workflow.add_edge("extract_indicators", "analysis_layer")
    workflow.add_edge("analysis_layer", "assess_confidence")
    workflow.add_edge("assess_confidence", "generate_questions")
    workflow.add_edge("generate_questions", "compile_brief")
    workflow.add_edge("compile_brief", END)
    workflow.add_edge("handle_failure", END)

    # Conditional edge: quality_check branches on document_failure
    workflow.add_conditional_edges(
        "quality_check",
        route_after_quality_check,
        {
            "extract_indicators": "extract_indicators",
            "handle_failure": "handle_failure"
        }
    )

    return workflow.compile()


# Singleton — import this in Streamlit and nodes
esg_graph = build_graph()
```

---

## 5. MVP Node Specifications

### Node 1: `ingest_document`

**File:** `app/agent/nodes/ingest.py`
**Purpose:** Convert raw PDF bytes into structured text and chunks for downstream processing.

**Reads from state:** `document_bytes`, `source_filename`
**Writes to state:** `document_text`, `document_chunks`, `num_pages`
**Calls:** PyMuPDF (`fitz`) only — no LLM, no ChromaDB

**Pseudocode:**
```python
import fitz  # PyMuPDF
from app.agent.state import AssessmentState


def ingest_document(state: AssessmentState) -> dict:
    """
    Extract text from PDF bytes.
    Returns only the fields this node is responsible for.
    LangGraph merges the returned dict into the existing state.
    """
    pdf_bytes = state["document_bytes"]

    # Open PDF from bytes
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    num_pages = len(doc)

    full_text = ""
    chunks = []

    for page_num, page in enumerate(doc):
        page_text = page.get_text("text")
        full_text += page_text

        # Create chunks of ~500 characters with metadata
        # Split page text into paragraphs and store with page reference
        paragraphs = [p.strip() for p in page_text.split("\n\n") if len(p.strip()) > 50]
        for para in paragraphs:
            chunks.append({
                "text": para,
                "page": page_num + 1,
                "section": None,      # Will be labelled by quality_check
                "is_table": False     # Table detection is done in table_extractor.py
            })

    doc.close()

    return {
        "document_text": full_text,
        "document_chunks": chunks,
        "num_pages": num_pages
    }
```

---

### Node 2: `quality_check`

**File:** `app/agent/nodes/quality.py`
**Purpose:** Assess whether the document is processable. Locate the BRSR section. Score confidence. Set `document_failure` if the document cannot be processed.

**Reads from state:** `document_text`, `document_chunks`
**Writes to state:** `is_machine_readable`, `brsr_section_found`, `brsr_section_text`, `extraction_confidence_score`, `document_failure`, `document_failure_reason`
**Calls:** No LLM, no ChromaDB — heuristic checks only

**Pseudocode:**
```python
from app.agent.state import AssessmentState


# Keywords used to locate the BRSR section in a larger annual report
BRSR_SECTION_MARKERS = [
    "business responsibility and sustainability report",
    "brsr",
    "national guidelines on responsible business conduct",
    "principle-wise performance",
    "ngrbc"
]


def quality_check(state: AssessmentState) -> dict:
    text = state["document_text"].lower()
    chunks = state["document_chunks"]

    # Check 1: Is the document machine-readable?
    # A scanned PDF produces very little extractable text per page
    chars_per_page = len(text) / max(state["num_pages"], 1)
    is_machine_readable = chars_per_page > 200   # Threshold: 200 chars/page minimum

    # Check 2: Find the BRSR section
    brsr_section_found = any(marker in text for marker in BRSR_SECTION_MARKERS)

    # Extract just the BRSR section text if found
    brsr_section_text = ""
    if brsr_section_found:
        brsr_section_text = extract_brsr_section(state["document_text"])

    # Check 3: Compute confidence score
    # Based on: readability + section found + proportion of extractable content
    score = 0.0
    if is_machine_readable:
        score += 0.4
    if brsr_section_found:
        score += 0.4
    if len(brsr_section_text) > 5000:   # Substantive BRSR content found
        score += 0.2

    # Check 4: Determine if document has failed
    document_failure = not is_machine_readable or not brsr_section_found
    failure_reason = None
    if not is_machine_readable:
        failure_reason = "Document appears to be scanned or image-based. Text extraction failed."
    elif not brsr_section_found:
        failure_reason = "BRSR section could not be located in the uploaded document."

    return {
        "is_machine_readable": is_machine_readable,
        "brsr_section_found": brsr_section_found,
        "brsr_section_text": brsr_section_text,
        "extraction_confidence_score": score,
        "document_failure": document_failure,
        "document_failure_reason": failure_reason
    }


def extract_brsr_section(full_text: str) -> str:
    """
    Locate and return the BRSR chapter from the full document text.
    Heuristic: find the section header and extract until the next major chapter.
    This is an approximation — improve iteratively using real BRSR PDFs.
    """
    # Implementation: search for BRSR header, extract ~30,000 chars forward
    # Refine based on actual BRSR PDFs encountered during testing
    lower = full_text.lower()
    start_idx = lower.find("business responsibility and sustainability report")
    if start_idx == -1:
        start_idx = lower.find("brsr")
    if start_idx == -1:
        return ""
    return full_text[start_idx: start_idx + 40000]
```

---

### Node 3: `extract_indicators`

**File:** `app/agent/nodes/extract.py`
**Purpose:** For each BRSR principle, use RAG to retrieve the indicator definitions, then prompt Claude to extract indicator states from the BRSR text.

**Reads from state:** `brsr_section_text`, `assessment_id`
**Writes to state:** `extracted_indicators`
**Calls:** Claude API (structured extraction), ChromaDB (indicator definitions)

**Pseudocode:**
```python
import json
from anthropic import Anthropic
from app.agent.state import AssessmentState
from app.rag.retriever import retrieve_indicator_context
from app.schemas.loader import load_brsr_schema


client = Anthropic()
BRSR_SCHEMA = load_brsr_schema()


def extract_indicators(state: AssessmentState) -> dict:
    """
    For each BRSR principle, extract the state of each essential indicator.
    Uses RAG to provide Claude with indicator definitions before asking it to extract.
    """
    brsr_text = state["brsr_section_text"]
    extracted = {}

    for principle_id, principle in BRSR_SCHEMA["principles"].items():
        # Retrieve indicator definitions from ChromaDB
        indicator_context = retrieve_indicator_context(
            principle_id=principle_id,
            framework="brsr_v2023"
        )

        # Build extraction prompt
        prompt = build_extraction_prompt(
            principle_name=principle["name"],
            indicator_definitions=indicator_context,
            brsr_text=brsr_text
        )

        # Call Claude for structured extraction
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response into structured indicator states
        extracted[principle_id] = parse_extraction_response(response.content[0].text)

    return {"extracted_indicators": extracted}


def build_extraction_prompt(principle_name, indicator_definitions, brsr_text):
    return f"""You are extracting ESG indicator data from a BRSR filing.

PRINCIPLE: {principle_name}

INDICATOR DEFINITIONS:
{indicator_definitions}

BRSR FILING TEXT (relevant section):
{brsr_text[:8000]}

For each indicator listed above, extract the following from the filing text:
- state: "disclosed" | "partially_disclosed" | "not_found"
- value: the actual disclosed value or text (empty string if not_found)
- citation: "Principle X, Indicator Y, Page Z" or "Not found in uploaded BRSR filing"

Respond ONLY with a valid JSON object. No preamble or explanation.
Example format:
{{
  "scope_1_emissions": {{
    "state": "disclosed",
    "value": "12,450 tCO2e",
    "citation": "Principle 6, Essential Indicator E-7, Page 142"
  }}
}}"""
```

---

### Node 4: `analysis_layer`

**File:** `app/agent/nodes/analysis.py`
**Purpose:** Run three classifiers: Scope 3 verdict, completeness assessment, gap detection. These call pure functions in `classification/` — the node orchestrates them and collects their outputs into state.

**Reads from state:** `extracted_indicators`, `brsr_section_text`
**Writes to state:** `scope3_verdict`, `completeness_results`, `gaps`
**Calls:** Claude API (for Scope 3 evidence extraction), `classification/` functions

**Pseudocode:**
```python
from app.agent.state import AssessmentState
from app.classification.scope3_classifier import classify_scope3
from app.classification.completeness import assess_completeness
from app.classification.gap_detector import detect_gaps


def analysis_layer(state: AssessmentState) -> dict:
    """
    Orchestrates three classifiers.
    Each classifier is a pure function — testable in isolation.
    """
    indicators = state["extracted_indicators"]
    brsr_text = state["brsr_section_text"]

    # Scope 3 verdict — applies the PRD decision tree
    scope3_verdict = classify_scope3(indicators, brsr_text)

    # Completeness — scores all 9 principles
    completeness_results = assess_completeness(indicators)

    # Gap detection — identifies and ranks top 5 gaps
    gaps = detect_gaps(
        indicators=indicators,
        scope3_level=scope3_verdict["level"],
        completeness=completeness_results
    )

    return {
        "scope3_verdict": scope3_verdict,
        "completeness_results": completeness_results,
        "gaps": gaps
    }
```

---

### Node 5: `assess_confidence`

**File:** `app/agent/nodes/confidence.py`
**Purpose:** Convert the raw confidence score from `quality_check` into a named level. Set the behavioural directive. Flag HITL if needed. This is a pure function — no LLM call.

**Reads from state:** `extraction_confidence_score`, `is_machine_readable`, `brsr_section_found`, `extracted_indicators`
**Writes to state:** `confidence_level`, `confidence_directive`, `hitl_flag`, `uncertain_fields`

**Pseudocode:**
```python
from app.agent.state import AssessmentState

HIGH_DIRECTIVE = (
    "Extraction quality is high. This brief can be used as the basis for "
    "procurement decision-making. Verify any specific claim by cross-referencing "
    "the cited section in the source document before acting on it."
)
MEDIUM_DIRECTIVE = (
    "Some sections had extraction uncertainty. Fields marked [⚠] in this brief "
    "should be manually verified against the source document before acting on them."
)
LOW_DIRECTIVE = (
    "Significant extraction limitations were detected. This brief must not be used "
    "for procurement decisions without full human review of the source BRSR filing."
)


def assess_confidence(state: AssessmentState) -> dict:
    score = state["extraction_confidence_score"]
    indicators = state.get("extracted_indicators", {})

    # Count how many indicators were successfully extracted
    total, found = 0, 0
    uncertain_fields = []
    for principle_id, principle_indicators in indicators.items():
        for ind_id, ind_data in principle_indicators.items():
            total += 1
            if ind_data.get("state") != "not_found":
                found += 1
            if ind_data.get("uncertain", False):
                uncertain_fields.append(f"{principle_id}.{ind_id}")

    extraction_ratio = found / total if total > 0 else 0.0

    # Determine level
    if score >= 0.8 and extraction_ratio >= 0.8 and not uncertain_fields:
        level = "high"
        directive = HIGH_DIRECTIVE
        hitl_flag = False
    elif score >= 0.5 and extraction_ratio >= 0.5:
        level = "medium"
        directive = MEDIUM_DIRECTIVE
        hitl_flag = len(uncertain_fields) > 2
    else:
        level = "low"
        directive = LOW_DIRECTIVE
        hitl_flag = True

    return {
        "confidence_level": level,
        "confidence_directive": directive,
        "hitl_flag": hitl_flag,
        "uncertain_fields": uncertain_fields
    }
```

---

### Node 6: `generate_questions`

**File:** `app/agent/nodes/questions.py`
**Purpose:** Generate 3–5 supplier-facing follow-up questions based on detected gaps. Uses Claude to produce natural, ready-to-use question text.

**Reads from state:** `gaps`, `supplier_name`
**Writes to state:** `followup_questions`
**Calls:** Claude API

**Pseudocode:**
```python
from anthropic import Anthropic
from app.agent.state import AssessmentState
import json

client = Anthropic()


def generate_questions(state: AssessmentState) -> dict:
    gaps = state["gaps"][:5]     # Maximum 5 questions
    supplier_name = state["supplier_name"]

    if not gaps:
        return {"followup_questions": []}

    gaps_text = json.dumps(gaps, indent=2)

    prompt = f"""You are generating supplier follow-up questions for {supplier_name}.

These gaps were identified in their BRSR filing:
{gaps_text}

Generate one follow-up question for each gap.
Rules:
- Write each question as if addressed directly to the supplier
- Name the specific missing item in each question
- Keep each question to 1–2 sentences
- Use professional but direct language
- Do NOT use internal terms like "G-01", "Critical", or "Level 2"

Respond ONLY with a JSON array. No preamble.
Format:
[
  {{
    "rank": 1,
    "question": "Your BRSR filing for FY2023–24 does not include...",
    "linked_gap_id": "G-01"
  }}
]"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    questions = json.loads(raw.replace("```json", "").replace("```", ""))

    return {"followup_questions": questions}
```

---

### Node 7: `compile_brief`

**File:** `app/agent/nodes/brief.py`
**Purpose:** Assemble all state outputs into the final structured brief dictionary. No LLM call — this is pure assembly.

**Reads from state:** All analysis outputs, confidence, questions
**Writes to state:** `brief`

**Pseudocode:**
```python
from datetime import datetime
from app.agent.state import AssessmentState

DISCLAIMER = (
    "This assessment is based solely on the uploaded BRSR filing. "
    "Disclosures in separate sustainability reports, CDP submissions, "
    "GRI reports, or supplementary documents were not reviewed and "
    "are not reflected in this brief."
)


def compile_brief(state: AssessmentState) -> dict:
    brief = {
        "disclaimer": DISCLAIMER,
        "header": {
            "supplier_name": state["supplier_name"],
            "source_filename": state["source_filename"],
            "assessment_id": state["assessment_id"],
            "generated_at": datetime.utcnow().isoformat(),
            "confidence_level": state["confidence_level"],
            "confidence_directive": state["confidence_directive"],
            "hitl_flag": state["hitl_flag"]
        },
        "completeness_assessment": state["completeness_results"],
        "scope3_verdict": state["scope3_verdict"],
        "gaps": state["gaps"],
        "followup_questions": state["followup_questions"],
        "uncertain_fields": state["uncertain_fields"]
    }

    return {"brief": brief}
```

---

### Node 8: `handle_failure`

**File:** `app/agent/nodes/failure.py`
**Purpose:** Produce a minimal error brief when the document cannot be processed.

**Pseudocode:**
```python
from app.agent.state import AssessmentState


def handle_failure(state: AssessmentState) -> dict:
    reason = state.get("document_failure_reason", "Unknown document processing error.")

    brief = {
        "disclaimer": "Assessment could not be completed.",
        "header": {
            "supplier_name": state["supplier_name"],
            "source_filename": state["source_filename"],
            "assessment_id": state["assessment_id"],
            "confidence_level": "low",
            "confidence_directive": (
                "Document processing failed. Please verify the uploaded file "
                "is a machine-readable BRSR PDF and try again."
            ),
            "hitl_flag": True
        },
        "error": reason,
        "completeness_assessment": [],
        "scope3_verdict": None,
        "gaps": [],
        "followup_questions": []
    }

    return {"brief": brief, "error": reason}
```

---

## 6. Technical Learning Dependencies

### Phase 1 — LangGraph Foundation

**Must learn before starting:**
- Python `TypedDict` — how to define a typed dictionary and why it matters for state
- LangGraph `StateGraph` — how to create a graph, add nodes, and add edges
- LangGraph `invoke()` — how to run a compiled graph with an initial state
- How LangGraph merges returned dicts into state (the "reducer" pattern)
- Anthropic SDK — `client.messages.create()` basics

**Can postpone:**
- Conditional edges (understand `add_edge` first, then add `add_conditional_edges`)
- `async` graph execution (not needed for MVP)
- LangGraph checkpointing / memory (V2 feature)
- LangSmith tracing (useful but not required)

**Recommended resources:**
- LangGraph Quickstart: https://langchain-ai.github.io/langgraph/tutorials/introduction/
- Focus on: "Building your first graph" and "State management" sections only

---

### Phase 2 — PDF Ingestion

**Must learn before starting:**
- PyMuPDF (`fitz`) — `open()`, `get_text()`, page iteration
- Python file handling — reading bytes, working with `io.BytesIO`
- Basic string manipulation for section detection

**Can postpone:**
- Table extraction (use text-only extraction first, add table handling in Phase 3)
- OCR (not needed — flag scanned PDFs with low confidence and move on)

---

### Phase 3 — ESG Extraction

**Must learn before starting:**
- How to structure a prompt for structured JSON output from Claude
- JSON parsing from LLM responses (`json.loads`, handling parse errors)
- Python `dict` manipulation for the `extracted_indicators` structure
- How to write a pure classification function (no side effects, testable)

**Can postpone:**
- Advanced prompt engineering (start with a simple extraction prompt and improve iteratively)
- Handling all 9 principles simultaneously (start with Principle 6 only, expand to all 9)

---

### Phase 4 — RAG Integration

**Must learn before starting:**
- ChromaDB Python client — `PersistentClient`, `get_or_create_collection`, `add()`, `query()`
- Embeddings — how `sentence-transformers` works, what a vector is conceptually
- LangChain `TextSplitter` — chunking text for indexing
- The difference between the two ChromaDB collections (static knowledge vs dynamic document)

**Can postpone:**
- Advanced retrieval strategies (MMR, hybrid search) — use simple similarity search for MVP
- Embedding model comparison — use `all-MiniLM-L6-v2` from sentence-transformers; it is fast and good enough
- pgvector migration (V2)

---

### Phase 5 — Streamlit UI

**Must learn before starting:**
- Streamlit basics: `st.title`, `st.file_uploader`, `st.spinner`, `st.json`, `st.expander`
- Streamlit session state: `st.session_state` for holding the brief between reruns
- How Streamlit reruns on every interaction (the core mental model)

**Can postpone:**
- Streamlit multi-page apps (`pages/` folder) — build a single-page app first, split later
- Custom CSS styling — functionality first, polish later

---

### Phase 6 — End-to-End Integration

**Must learn before starting:**
- Everything from Phases 1–5
- How to wire Streamlit → LangGraph → output display in one flow
- Basic error handling in Python (`try/except` in node functions)

**Can postpone:**
- JSON persistence to disk (`utils/storage.py`) — start by just displaying the brief in Streamlit and not saving
- Assessment history page — add after the core brief generation is working

---

## 7. Weekly Build Plan

> **Important:** Each day has one clearly defined task. Stop when the task is done rather than jumping ahead. The hardest week is Week 1 — after that, each phase builds on working code.

---

### Week 1 — LangGraph Foundation + PDF Ingestion (Phases 1 & 2)

**Day 1 — LangGraph basics (Phase 1 task)**
- Complete the First Coding Task in Section 8 of this document
- Goal: understand TypedDict state, nodes, edges, and `graph.invoke()`
- Do not add ESG logic yet

**Day 2 — Extend Phase 1 pipeline**
- Add a conditional edge to your Phase 1 pipeline
- If text is < 50 words → route to a `too_short` node
- If text is ≥ 50 words → route to a `summarise` node
- Verify both paths work with `graph.invoke()`

**Day 3 — Project setup**
- Create the full folder structure from Section 3
- Set up `requirements.txt` and virtual environment
- Configure `.env` with `ANTHROPIC_API_KEY`
- Create `app/agent/state.py` with the full `AssessmentState` definition
- Create `app/agent/graph.py` with placeholder node functions (each just returns an empty dict)
- Verify the graph compiles without errors

**Day 4 — `ingest_document` node (Phase 2)**
- Install PyMuPDF: `pip install pymupdf`
- Implement `app/agent/nodes/ingest.py`
- Test it directly: `python -c "from app.agent.nodes.ingest import ingest_document; ..."`
- Do not run it through LangGraph yet — test the function in isolation first

**Day 5 — `quality_check` node + conditional edge (Phase 2)**
- Implement `app/agent/nodes/quality.py`
- Implement `app/agent/edges/routing.py`
- Wire both nodes into the graph in `graph.py`
- Test with a real BRSR PDF: `graph.invoke({"document_bytes": pdf_bytes, ...})`
- Confirm: document failure routes to `handle_failure`, success continues

**Day 6–7 — Buffer / debugging**
- Debug PDF parsing on 2–3 real BRSR filings
- Tune the `extract_brsr_section` heuristic
- Fix any state field issues (missing keys, type errors)

**Week 1 acceptance criterion:** Given a real BRSR PDF, the LangGraph pipeline extracts text, locates the BRSR section, scores confidence, and routes correctly.

---

### Week 2 — ESG Extraction + BRSR Schema (Phase 3)

**Day 8 — BRSR schema JSON**
- Create `app/schemas/brsr_v2023.json`
- Start with Principle 6 only (Environment) — 10–12 essential indicators
- Structure: `{"principles": {"principle_6": {"name": "Environment", "indicators": {...}}}}`
- Create `app/schemas/loader.py` to load and validate this file

**Day 9 — Scope 3 classifier (pure function)**
- Implement `app/classification/scope3_classifier.py`
- Code the full decision tree from the PRD (Section 11) as a pure Python function
- Write unit tests in `tests/test_scope3_classifier.py` with 5 different input scenarios
- Verify all 4 levels + Materiality Claim trigger correctly

**Day 10 — Completeness assessor (pure function)**
- Implement `app/classification/completeness.py`
- Test against synthetic extracted_indicators data

**Day 11 — Gap detector (pure function)**
- Implement `app/classification/gap_detector.py`
- Include G-01 through G-05 (Critical gaps) for MVP
- Test gap ranking logic

**Day 12 — `extract_indicators` node (without RAG)**
- Implement `app/agent/nodes/extract.py` using a hardcoded prompt (no ChromaDB yet)
- Test Claude extraction on real BRSR Principle 6 text
- Verify output matches the `extracted_indicators` structure

**Day 13 — `analysis_layer` node**
- Implement `app/agent/nodes/analysis.py`
- Wire all three classifiers together
- Run end-to-end through the graph up to this node

**Day 14 — Buffer / testing**
- Run the pipeline on 3 real BRSR filings
- Fix extraction failures
- Note which BRSR PDFs produce the most parsing problems (document this)

**Week 2 acceptance criterion:** Given a BRSR PDF, the pipeline correctly classifies Scope 3 readiness level, produces a completeness assessment for all 9 principles, and identifies the top 5 gaps.

---

### Week 3 — RAG Integration (Phase 4)

**Day 15 — ChromaDB setup**
- Install: `pip install chromadb sentence-transformers`
- Create `app/rag/client.py` with a local persistent ChromaDB client pointing to `data/chromadb/`
- Create `app/rag/collections.py` defining the two collections

**Day 16 — Knowledge base content**
- Write `knowledge_base/brsr/principles/principle_6_environment.md`
- Write `knowledge_base/brsr/indicators/essential_indicators.md` (Principle 6 section)
- Write `knowledge_base/esg_concepts/scope3_guidance.md`
- Keep each file to 500–800 words — focused, dense, factual

**Day 17 — Index knowledge base into ChromaDB**
- Implement `app/rag/loader.py`
- Load all markdown files from `knowledge_base/`, chunk them, embed them, store in `framework_knowledge` collection
- Test retrieval: query "What does Principle 6 Essential Indicator E-7 require?"
- Verify you get relevant indicator definitions back

**Day 18 — Document chunk indexing**
- Implement document chunk indexing in the `extract_indicators` node
- Before extraction, index the uploaded document's chunks into `document_chunks` collection
- Implement `app/rag/retriever.py` with `retrieve_indicator_context()` and `retrieve_from_doc()`

**Day 19 — Connect RAG to extraction**
- Update `extract_indicators` to call `retrieve_indicator_context()` before building the extraction prompt
- Test: the prompt now includes ChromaDB-retrieved definitions instead of hardcoded text
- Verify extraction quality improves on Principle 6

**Day 20 — `assess_confidence` and `generate_questions` nodes**
- Implement `app/agent/nodes/confidence.py`
- Implement `app/agent/nodes/questions.py`
- Run the full graph end-to-end and inspect the complete state output

**Day 21 — Buffer / RAG tuning**
- Add more knowledge base content for Principles 1–5 and 7–9
- Tune chunk sizes if retrieval quality is poor
- Fix any ChromaDB client errors

**Week 3 acceptance criterion:** ChromaDB is running locally with the BRSR knowledge base indexed. Extraction uses RAG context. The full pipeline runs end-to-end and produces a complete `brief` in state.

---

### Week 4 — Streamlit UI + End-to-End MVP (Phases 5 & 6)

**Day 22 — Basic Streamlit app**
- Create `app/main.py` as a single-page Streamlit app
- Add: file uploader, supplier name input, submit button
- On submit: call `esg_graph.invoke()` with uploaded PDF bytes
- Display raw `st.json(brief)` output — ugly but functional

**Day 23 — Brief display components**
- Implement `app/ui/components/confidence_banner.py`
- Implement `app/ui/components/scope3_badge.py`
- Implement `app/ui/components/completeness_table.py`
- Replace `st.json()` with these components

**Day 24 — Gap and question display**
- Implement `app/ui/components/gap_card.py`
- Implement `app/ui/components/question_card.py`
- Render all 5 gaps and all 5 questions in the brief viewer

**Day 25 — Processing feedback + error handling**
- Add `st.spinner()` while the graph is running
- Add progressive status messages using `st.status()`
- Handle document failure: display the error message clearly

**Day 26 — JSON persistence and history**
- Implement `app/utils/storage.py` to save completed briefs to `data/assessments/`
- Add a simple history view: list past assessments, click to reload a brief

**Day 27 — End-to-end validation**
- Run the complete MVP against 5 real NSE top-1000 BRSR filings
- For each filing, verify the Scope 3 verdict matches manual review
- Fix any issues found

**Day 28 — Portfolio polish**
- Write `README.md` with: project description, architecture overview, setup instructions, demo screenshot
- Add `.env.example`
- Clean up any debug print statements
- Final run of all acceptance criteria checks

**Week 4 acceptance criterion:** See Section 9.

---

## 8. First Coding Task

> **Complete this today. Do not skip it.**
> This task teaches the three most important LangGraph concepts before you write any ESG logic.

---

### Task: Build a `TextQualityPipeline`

**What you are building:**
A 3-node LangGraph pipeline that:
1. Receives a block of text as input
2. Checks if the text is long enough to summarise (≥ 50 words)
3. If too short: returns a "too short to summarise" message
4. If adequate length: calls Claude to summarise it in one sentence
5. Returns the final result

**What you will learn:**
- How to define a `TypedDict` state
- How to write a node function (receives state dict, returns dict of updates)
- How LangGraph merges returned dicts into the existing state
- How to define a conditional edge
- How to compile and invoke a graph

**Do not add:** database, ChromaDB, PDF parsing, ESG logic, Streamlit. One file only.

---

```python
# text_quality_pipeline.py
# Run with: python text_quality_pipeline.py

import os
from typing import TypedDict, Literal, Optional
from langgraph.graph import StateGraph, END
from anthropic import Anthropic

# ── 1. INSTALL DEPENDENCIES ────────────────────────────────────────────────
# pip install langgraph anthropic
# Set ANTHROPIC_API_KEY in your environment before running.

client = Anthropic()


# ── 2. STATE DEFINITION ────────────────────────────────────────────────────
# This is the shared state object. Every node reads from and writes to this.
# TypedDict gives you type hints — LangGraph works with plain dicts too,
# but TypedDict makes your code readable and debuggable.

class TextPipelineState(TypedDict):
    # Input
    input_text: str

    # Written by check_length node
    word_count: int
    is_adequate: bool                              # True if >= 50 words

    # Written by summarise or too_short node
    result: Optional[str]


# ── 3. NODE FUNCTIONS ──────────────────────────────────────────────────────
# Each node is a plain Python function.
# It receives the current state dict.
# It returns a dict of ONLY the fields it wants to update.
# LangGraph merges this returned dict into the existing state automatically.
# You never return the full state — only your changes.

def check_length(state: TextPipelineState) -> dict:
    """
    Node 1: Count words and decide if the text is long enough to summarise.
    No LLM call — pure Python logic.
    """
    text = state["input_text"]
    word_count = len(text.split())
    is_adequate = word_count >= 50

    print(f"[check_length] Word count: {word_count}. Adequate: {is_adequate}")

    # Return ONLY the fields this node writes
    return {
        "word_count": word_count,
        "is_adequate": is_adequate
    }


def summarise(state: TextPipelineState) -> dict:
    """
    Node 2a: Text is long enough — summarise it using Claude.
    """
    text = state["input_text"]
    print(f"[summarise] Calling Claude to summarise {state['word_count']} words...")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": f"Summarise the following text in exactly one sentence:\n\n{text}"
        }]
    )

    summary = response.content[0].text.strip()
    print(f"[summarise] Result: {summary}")

    return {"result": f"SUMMARY: {summary}"}


def too_short(state: TextPipelineState) -> dict:
    """
    Node 2b: Text is too short — return a message without calling Claude.
    """
    print(f"[too_short] Text has only {state['word_count']} words. Minimum is 50.")
    return {"result": f"TEXT TOO SHORT ({state['word_count']} words). Minimum is 50 words."}


# ── 4. ROUTING FUNCTION ────────────────────────────────────────────────────
# This function is called by LangGraph after check_length completes.
# It reads the current state and returns the name of the next node.

def route_by_length(state: TextPipelineState) -> str:
    """
    Conditional routing: decide which node to go to next.
    Return the node NAME as a string — must match a registered node name.
    """
    if state["is_adequate"]:
        return "summarise"
    else:
        return "too_short"


# ── 5. GRAPH ASSEMBLY ──────────────────────────────────────────────────────

def build_pipeline():
    """Build, compile, and return the LangGraph pipeline."""

    # Create a graph that uses TextPipelineState as its state type
    workflow = StateGraph(TextPipelineState)

    # Register nodes: (node_name, node_function)
    # node_name is the string used in routing and edge definitions
    workflow.add_node("check_length", check_length)
    workflow.add_node("summarise", summarise)
    workflow.add_node("too_short", too_short)

    # Set the first node that runs when graph.invoke() is called
    workflow.set_entry_point("check_length")

    # Conditional edge: after check_length, call route_by_length to decide what's next
    # The dict maps each possible return value of route_by_length to a node name
    workflow.add_conditional_edges(
        "check_length",              # Source node
        route_by_length,             # Routing function
        {
            "summarise": "summarise",    # If route_by_length returns "summarise" → go to "summarise"
            "too_short": "too_short"     # If route_by_length returns "too_short" → go to "too_short"
        }
    )

    # Both terminal nodes go straight to END
    workflow.add_edge("summarise", END)
    workflow.add_edge("too_short", END)

    # Compile the graph — this validates the structure and returns a runnable object
    return workflow.compile()


# ── 6. RUN THE PIPELINE ────────────────────────────────────────────────────

if __name__ == "__main__":
    pipeline = build_pipeline()

    # Test 1: Short text (should route to too_short)
    print("\n" + "=" * 60)
    print("TEST 1: Short text")
    print("=" * 60)
    short_result = pipeline.invoke({
        "input_text": "This is a very short piece of text.",
        "word_count": 0,        # LangGraph needs all TypedDict keys at invocation
        "is_adequate": False,   # These will be overwritten by check_length
        "result": None
    })
    print(f"Final result: {short_result['result']}")

    # Test 2: Long text (should route to summarise and call Claude)
    print("\n" + "=" * 60)
    print("TEST 2: Long text")
    print("=" * 60)
    long_text = """
    Business Responsibility and Sustainability Reporting represents a significant
    evolution in corporate disclosure requirements in India. Mandated by SEBI for
    the top 1000 listed companies by market capitalisation, BRSR requires companies
    to disclose their performance across nine principles of the National Guidelines on
    Responsible Business Conduct. These principles cover ethics, sustainable products,
    employee wellbeing, stakeholder responsiveness, human rights, environmental
    protection, public policy, inclusive growth, and consumer responsibility.
    The framework is designed to create a standardised basis for ESG assessment
    and improve transparency in the Indian capital markets.
    """
    long_result = pipeline.invoke({
        "input_text": long_text,
        "word_count": 0,
        "is_adequate": False,
        "result": None
    })
    print(f"Final result: {long_result['result']}")

    # Inspect the full final state
    print("\n" + "=" * 60)
    print("FULL FINAL STATE (Test 2):")
    print("=" * 60)
    for key, value in long_result.items():
        print(f"  {key}: {value}")
```

---

**After you run this successfully:**

1. Add a fourth node `count_sentences` that runs after `summarise` and counts how many sentences are in the summary. Make it always route to `END`. Observe how state accumulates.

2. Change `route_by_length` to accept a third option: if word count is between 50 and 100, return `"needs_context"` and add a `needs_context` node that asks Claude for a longer summary. Wire the new conditional edge.

3. Look at `long_result` — every field you set in every node is in the final state. This is the mental model for the entire ESG pipeline.

---

## 9. Acceptance Criteria

### Phase 1 Acceptance Criteria

| Criterion | How to verify |
|---|---|
| The `TextQualityPipeline` from Section 8 runs without errors | `python text_quality_pipeline.py` exits cleanly with output |
| Short text routes to `too_short` node | Input < 50 words produces "TEXT TOO SHORT" in result |
| Long text routes to `summarise` node | Input ≥ 50 words produces a Claude-generated summary |
| The full AssessmentState TypedDict is defined in `app/agent/state.py` | File exists, all fields present, `from app.agent.state import AssessmentState` succeeds |
| The LangGraph graph compiles | `from app.agent.graph import esg_graph` succeeds without error |
| All 8 placeholder node functions are registered | `esg_graph.get_graph().nodes` returns all 8 node names |

---

### Phase 2 Acceptance Criteria

| Criterion | How to verify |
|---|---|
| `ingest_document` extracts text from a real BRSR PDF | `document_text` in state has > 10,000 characters |
| `quality_check` correctly identifies a machine-readable BRSR | `is_machine_readable = True`, `brsr_section_found = True` for a standard NSE filing |
| `quality_check` triggers document failure on a scanned PDF | `document_failure = True` for an image-only PDF |
| Conditional routing works in the full graph | A failed document routes to `handle_failure`; a good document routes to `extract_indicators` |
| `handle_failure` produces a brief with an error message | `state["brief"]["error"]` is populated with the failure reason |

---

### Phase 3 Acceptance Criteria

| Criterion | How to verify |
|---|---|
| Scope 3 classifier returns correct level for 5 test cases | Unit tests in `test_scope3_classifier.py` all pass |
| Intensity-only Scope 3 figures return Level 1 (Claim Only), not Level 2 | Specific unit test case for intensity input returns `claim_only` |
| Materiality Claim triggers separate state (not Level 0) | Input containing "Scope 3 is not material" returns `materiality_claim` |
| `analysis_layer` produces all three outputs | `scope3_verdict`, `completeness_results`, and `gaps` are populated in state |
| Top gap is always G-01 when Scope 3 is Level 0 or Level 1 | Verified on 3 real BRSR filings with absent or claim-only Scope 3 |

---

### MVP Completion Acceptance Criteria

These are the final criteria the MVP must pass before being considered complete and portfolio-ready.

| # | Criterion | How to verify |
|---|---|---|
| AC-01 | A real BRSR PDF can be uploaded through the Streamlit UI | No errors on upload; file is received and processed |
| AC-02 | Processing completes within 90 seconds | Time `graph.invoke()` on a 200-page annual report PDF |
| AC-03 | The disclaimer appears at the top of every brief | Visually inspect output for all 5 test PDFs |
| AC-04 | Confidence indicator (High / Medium / Low) appears on every brief | Inspect 5 diverse PDFs; both high and low confidence cases confirmed |
| AC-05 | All 9 BRSR principles appear in the completeness table | Inspect output structure; count principle entries |
| AC-06 | Scope 3 verdict is one of the 5 valid states | Run on 5 PDFs covering multiple expected states |
| AC-07 | Intensity-only Scope 3 is never classified as Partial | Confirm on a PDF with ratio-only Scope 3 disclosure |
| AC-08 | Top 5 gaps are produced with BRSR citations | Each gap has `brsr_reference` and `citation` populated |
| AC-09 | 3–5 follow-up questions are generated per brief | Question count is between 3 and 5 in all outputs |
| AC-10 | Every factual claim references a source section or "Not found..." | Manually check 10 randomly selected claims across 3 briefs |
| AC-11 | Low Confidence brief displays directive before other content | Upload a scanned PDF; verify directive is first visible element |
| AC-12 | Scope 3 classification matches manual review | Domain expert (you) reviews same PDF and agrees with verdict in ≥ 4 of 5 test cases |
| AC-13 | The app runs from a clean environment with `pip install -r requirements.txt` + `streamlit run app/main.py` | Test in a fresh virtual environment |
| AC-14 | README contains setup instructions, architecture overview, and at least one screenshot | Visually inspect the README on GitHub |

---

*Document version: 1.0*
*Status: Approved for implementation*
*Next action: Complete Section 8 First Coding Task today*
