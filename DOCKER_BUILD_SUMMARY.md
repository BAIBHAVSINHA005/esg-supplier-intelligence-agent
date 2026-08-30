# Docker Build Summary — Supplier ESG Intelligence API V1

**Date:** 2026-08-30  
**Status:** Local Docker build and end-to-end container validation complete;
cloud deployment not complete

This file is a concise implementation record. The maintained build, run,
validation, configuration, and troubleshooting instructions live in
[`docs/DOCKER_DEPLOYMENT.md`](docs/DOCKER_DEPLOYMENT.md).

## Delivered

- `Dockerfile` using `python:3.12-slim`
- `.dockerignore` with development files, caches, secrets, and tests excluded
- CPU-only PyTorch `2.13.0+cpu` installed from the official PyTorch CPU index
- build-time import validation confirming PyTorch has no CUDA runtime
- FastAPI served by one Uvicorn worker on port 8000
- Docker health check against `GET /health`
- runtime `OPENAI_API_KEY` injection; no key baked into the image

## Verified

- image builds successfully
- CPU-only dependency resolution succeeds
- container starts successfully
- `GET /health` returns HTTP 200 from the container
- Swagger/OpenAPI loads and exposes the multipart PDF assessment contract
- `POST /v1/assessments` returns the explicit nested Pydantic response shape
- a real Birla BRSR completed through Swagger → FastAPI → Docker → LangGraph →
  RAG/LLM → typed ESG brief with HTTP 200 and the expected business output

Containerization did not change the LangGraph workflow, extraction, RAG,
deterministic ESG logic, shared assessment service, or UI behavior.

## Remaining before `v1.0.0`

- keep maintained regression validation green
- finish documentation, demo assets, and release hardening
- validate a third weaker/disclosure-poor BRSR if retained
- deploy the image to the selected cloud runtime and verify its endpoints
- create the final release commit and `v1.0.0` tag

Local Docker success is not a claim of completed cloud or production
deployment.
