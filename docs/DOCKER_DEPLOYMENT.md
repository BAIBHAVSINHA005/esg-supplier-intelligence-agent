# Docker Deployment Guide: Supplier ESG Intelligence API

**Status:** Local image build and end-to-end container validation complete;
cloud deployment not yet complete.

This is the maintained Docker runbook. `DOCKER_BUILD_SUMMARY.md` is retained as
a concise historical summary and points here for operational instructions.

## Summary of Changes

### Files Created/Modified
1. **`Dockerfile`** — Production container image definition
2. **`.dockerignore`** — Exclude unnecessary files from build context

## Docker Configuration Details

### Base Image
- **Image**: `python:3.12-slim`
- **Rationale**: 
  - Python 3.12 is the verified container runtime
  - Slim variant reduces image size (~150MB vs ~900MB with full image)
  - Includes minimal OS dependencies for security and performance

### System Dependencies
Installed in container:
- `build-essential` — Required for compiling Python packages from source
- `curl` — Used for health checks

### Python Dependencies
- Installed from `requirements.txt` 
- No caching enabled (`--no-cache-dir`) to reduce image size
- All production dependencies included (FastAPI, Uvicorn, LangGraph, ChromaDB, OpenAI, etc.)
- CPU-only PyTorch `2.13.0+cpu` is installed from the official CPU wheel index
  before the remaining requirements, avoiding CUDA/NVIDIA runtime packages
- the build verifies imports and asserts that CUDA is not enabled

### Runtime Directories
Created with write permissions:
- `vector_db/` — Persistent Chroma vector database storage

### Health Check
- **Endpoint**: `GET /health`
- **Interval**: 30 seconds
- **Timeout**: 5 seconds
- **Start period**: 10 seconds
- **Retries**: 3 failures before marking unhealthy

### Uvicorn Configuration
- **Host**: `0.0.0.0` (listen on all interfaces)
- **Port**: `8000` (industry standard for FastAPI)
- **Workers**: `1` (single worker process)
  - Suitable for I/O-bound work (LLM calls, file uploads)
  - Increase to `2-4` for CPU-bound workloads or higher concurrency
- **Reload**: Disabled (not suitable for production)

---

## Build Commands

### Build the image with single tag
```bash
docker build -t esg-supplier-intelligence-api:v1 .
```

### Build with multiple tags (recommended)
```bash
docker build \
  -t esg-supplier-intelligence-api:v1 \
  -t esg-supplier-intelligence-api:latest \
  .
```

## Run Commands

### Minimal run (local testing)
```bash
docker run \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your-key-here \
  esg-supplier-intelligence-api:v1
```

### Production run with volume mounts
```bash
docker run \
  --name esg-api \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your-api-key \
  -v /host/path/vector_db:/app/vector_db \
  -d \
  esg-supplier-intelligence-api:v1
```

### Run with environment file
```bash
docker run \
  --name esg-api \
  -p 8000:8000 \
  --env-file .env.docker \
  -v /host/path/vector_db:/app/vector_db \
  -d \
  esg-supplier-intelligence-api:v1
```

Example `.env.docker`:
```
OPENAI_API_KEY=sk-...your-key...
```

---

## Validation Steps

### 1. Check image build
```bash
docker images | grep esg-supplier-intelligence-api
```

### 2. Start container
```bash
docker run --name test-api -p 8000:8000 -e OPENAI_API_KEY=test esg-supplier-intelligence-api:v1
```

### 3. Test /health endpoint
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "supplier-esg-intelligence-api"
}
```

### 4. Test API documentation
Open in browser:
```
http://localhost:8000/docs
```

This opens the interactive Swagger UI where you can test endpoints.

### 5. Test file upload endpoint (from host)
```bash
curl -X POST http://localhost:8000/v1/assessments \
  -F "file=@sample.pdf" \
  -F "supplier_name=Test Supplier"
```

### 6. Check container logs
```bash
docker logs test-api
```

### 7. Stop container
```bash
docker stop test-api
docker rm test-api
```

---

## Environment Variables Required at Runtime

### Required
- **`OPENAI_API_KEY`** — OpenAI API key for LLM extraction
  - Format: `sk-...`
  - No default; must be provided

### Optional (python-dotenv support)
If a `.env` file exists in the container's working directory (`/app`), python-dotenv will load it. This is useful for development but not recommended for production—use Docker's `-e` flag or `--env-file` instead.

---

## Storage and Persistence

### Vector Database (`vector_db/`)
- **Purpose**: Persistent ChromaDB storage for embeddings
- **Strategy**:
  - **Development**: Use container-local storage (ephemeral)
  - **Production**: Mount a host volume to persist across container restarts
  - **Example**: `-v /data/esg-vector-db:/app/vector_db`

## Embedding Model Behavior

### Sentence Transformers: `all-MiniLM-L6-v2`
- **Download**: Lazy-loaded on first embedding call
- **Size**: ~27 MB
- **Location**: Cached in `~/.cache/huggingface/hub/` on first run
- **Persistence**: With volume mount, model cache persists (recommended)
- **First request**: May take 2-5 seconds to download and initialize
- **Subsequent requests**: Fast (<100ms per chunk)

### Container First-Run Behavior
1. Container starts → Uvicorn listens on port 8000
2. First assessment request received
3. Sentence-transformers model downloaded (~27 MB)
4. Model cached in container
5. Embedding generation proceeds

**Optimization tip**: To pre-warm the model, make a dummy assessment request after deployment.

---

## OpenAI Integration

### Extraction Pipeline
- **LLM**: OpenAI (Responses API for structured extraction)
- **Retry Logic**: Targeted rate-limit retry, maximum 3 attempts; server delay
  information is preferred before exponential fallback
- **Cost**: ~$0.10–$0.50 per assessment (varies by document length)
- **Timeout**: Default request timeout applies

### Environment Setup
```bash
# During docker run
docker run \
  -e OPENAI_API_KEY=sk-your-actual-key \
  esg-supplier-intelligence-api:v1
```

### API Key Security
- **Never** bake API keys into the Docker image
- **Always** pass via environment variable at runtime
- **Use** Docker secrets for Swarm or Kubernetes for multi-node deployments
- **Rotate** keys regularly

---

## Resource Recommendations

### CPU
- **Minimum**: 2 cores
- **Recommended**: 4 cores (for concurrent requests + embedding generation)

### Memory
- **Minimum**: 2 GB
- **Recommended**: 4–8 GB (embedding model is memory-efficient but requests are I/O-bound)
- **Note**: Sentence-transformers loads into memory; budget ~300 MB

### Disk
- **Base image + dependencies**: ~1.2 GB
- **Vector database**: Grows with documents; start with 2 GB

### Example docker-compose (optional, future reference)
```yaml
version: '3.8'
services:
  esg-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./vector_db:/app/vector_db
    restart: unless-stopped
```

---

## Deployment Checklist

- [x] `Dockerfile` created and reviewed
- [x] `.dockerignore` created to exclude unnecessary files
- [x] `docker build` completes without errors on Python 3.12
- [x] CPU-only PyTorch installation validated
- [ ] Image tags created (v1, latest)
- [x] Container starts with `docker run`
- [x] `/health` endpoint responds with HTTP 200
- [x] `/docs` endpoint accessible (Swagger UI)
- [x] `/v1/assessments` accepts multipart PDF upload
- [x] Real Birla BRSR returns HTTP 200 and the expected typed ESG brief
- [ ] Volume mounts configured for production persistence
- [ ] `OPENAI_API_KEY` environment variable set
- [x] Local container logs reviewed
- [ ] Health check configured in orchestrator (Kubernetes, Docker Swarm, etc.)
- [ ] Cloud deployment completed and verified

---

## Known Limitations & Future Improvements

1. **Single-worker Uvicorn**: Suitable for initial deployment; increase workers if latency becomes an issue
2. **No request queue**: Long-running assessments block the worker; consider adding async task queue (Celery + Redis) in future
3. **Embedding model pre-warming**: First assessment request will be slow; consider health-check trigger or init script
4. **No log aggregation**: Logs output to stdout; use container logging driver (awslogs, splunk, etc.) for production
5. **Chroma persistence**: Currently uses SQLite; consider managed vector DB (Pinecone, Weaviate) for scale

---

## Troubleshooting

### Container exits immediately
```bash
docker logs <container-id>
```
Check for missing dependencies or Python import errors.

### `/health` returns 500
- Check container logs for initialization errors
- Ensure dependencies in `requirements.txt` are compatible

The health endpoint itself does not call OpenAI and does not require a valid API
key to return the process-health response.

### Slow first assessment request (30+ seconds)
- Expected behavior on first run (model download + initialization)
- Subsequent requests are faster
- Use separate warm-up request to hide latency from end users

### File upload fails
- Verify PDF file size < container memory
- Check `OPENAI_API_KEY` is valid

### Vector database grows too large
- Implement periodic cleanup of old embeddings
- Consider migration to managed vector DB
- Monitor `vector_db/` disk usage

---

## Next Steps

1. **Keep the maintained regression suite green**
2. **Push the verified image to a registry** (Docker Hub, ECR, etc.):
   ```bash
   docker tag esg-supplier-intelligence-api:v1 <registry>/esg-supplier-intelligence-api:v1
   docker push <registry>/esg-supplier-intelligence-api:v1
   ```
3. **Deploy to the selected cloud runtime**; this step is not yet complete
4. **Configure persistent storage** for `vector_db/` if required
5. **Set up monitoring** for container health, logs, and performance
6. **Verify `/health`, Swagger/OpenAPI, and a real assessment in the cloud**
7. **Complete the `v1.0.0` release/tag**

---

## References

- [Docker Documentation](https://docs.docker.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [ChromaDB Persistence](https://docs.trychroma.com/deployment/persistent-storage)
- [Sentence Transformers Caching](https://www.sbert.net/docs/models/model_overview.html)
