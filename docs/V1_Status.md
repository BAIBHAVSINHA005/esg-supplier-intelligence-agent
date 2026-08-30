# Supplier ESG Intelligence Agent — V1 Status

**Project:** Supplier ESG Intelligence Agent

**Version:** V1 release candidate

**Status:** Core intelligence and local Docker delivery complete; release work remains
**Last updated:** August 2026

## Current V1 objective

V1 demonstrates an end-to-end, evidence-grounded workflow that converts a
machine-readable Indian BRSR filing into a typed, procurement-ready ESG
Intelligence Brief. The current assessment depth is BRSR Principle 6, with
particular emphasis on Scope 3 disclosure usability, evidence traceability,
supplier information gaps, and procurement follow-up.

## Completed V1 work

### Intelligence and reliability

- LangGraph assessment workflow
- PDF ingestion, BRSR detection, and document-quality checks
- Chroma indexing with document-scoped and indicator-specific retrieval
- bounded chunk subdivision for embedding reliability
- structured LLM extraction and deterministic ESG analysis
- Scope 3 readiness, completeness, confidence, and HITL logic
- `not_found` separated from `extraction_error`
- bounded OpenAI rate-limit retry behavior
- strict evidence provenance without fabricated sources
- supplier-specific questions and deterministic procurement recommendations
- typed ESG Intelligence Brief generation
- Streamlit and Gradio presentation layers

### API and container delivery

- FastAPI `GET /health`
- FastAPI multipart `POST /v1/assessments`
- explicit nested Pydantic public response contract
- OpenAPI schema and Swagger upload flow validated
- synchronous service execution kept behind the shared assessment boundary
- Docker image built successfully on Python 3.12
- CPU-only PyTorch dependency path validated
- Uvicorn/FastAPI container startup validated
- container `/health` returned HTTP 200
- real Birla BRSR completed through Swagger → FastAPI → Docker → LangGraph →
  RAG/LLM → typed brief with HTTP 200 and expected business output

## Validation baseline

### Automated regression suite

```text
57 passed
0 failed
11 subtests passed
16 warnings
```

The warnings are deprecation/cache warnings and did not fail the maintained
suite. Coverage includes retrieval regressions, chunk subdivision, document
isolation, structured extraction, API contracts, Scope 3 state consistency,
failure handling, confidence/HITL, evidence grounding, recommendations, and
supplier-name fallback.

### Real-company validation

- **Reliance Industries:** waste retrieval hardening, Scope 3 `not_found`, high
  confidence, and grounded procurement output validated.
- **Birla Corporation Limited:** supplier identity, `18,09,403.78 tCO2e`
  Scope 3 disclosure, Partial classification, `31,223.96 MT` total waste, and
  grounded questions/recommendations validated. The Birla filing also passed
  the complete Dockerized API path.

## V1 scope and readiness

| Area | Status |
| --- | --- |
| Core LangGraph/RAG/ESG intelligence | Complete |
| Reliability and evidence grounding | Complete |
| Procurement-facing brief | Complete |
| FastAPI and typed public contract | Complete |
| OpenAPI/Swagger validation | Complete |
| Local Docker build and runtime validation | Complete |
| Real Dockerized Birla assessment | Complete |
| Cloud deployment | Not complete |
| Final `v1.0.0` release/tag | Not complete |

## Remaining before `v1.0.0`

1. keep the maintained regression suite green
2. finish documentation, demo assets, and release hardening
3. validate a third weaker/disclosure-poor BRSR if that acceptance step is retained
4. complete cloud deployment and verify the deployed health/assessment paths
5. create the final release commit and `v1.0.0` tag

No additional product features are required for V1.

## Deferred beyond V1

### V2 — persistent multi-supplier operation

- PostgreSQL/Supabase persistence and assessment history
- pgvector migration if evaluation justifies it
- supplier comparison
- formal evaluation and runtime observability
- checkpointing/persistence
- authentication and multi-user access
- MCP exposure of stable capabilities
- supplier-response workflows

### V3 and future

- controlled specialist-agent and verifier/critic workflows
- supplier outreach automation
- broader ESG document/framework support
- enterprise portfolio analysis, benchmarking, and integrations

## Release decision

V1 is functionally complete for local containerized execution. The release is
not yet final because cloud deployment, final hardening, and the `v1.0.0` tag
remain outstanding.
