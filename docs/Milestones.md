## Milestone: MVP-2 — End-to-End RAG Pipeline
**Status:** ✅ Completed
**Date:** July 2026

### Completed
- PDF ingestion and document parsing
- Chunk enhancement with UUID-based chunk IDs
- ChromaDB indexing integrated into LangGraph
- Semantic retrieval from uploaded documents
- ESG indicator extraction
- Analysis layer
- Confidence assessment
- Follow-up question generation
- ESG Intelligence Brief compilation
- End-to-end LangGraph execution verified

### Key Engineering Fixes
- Added explicit `index_document` node to the graph
- Fixed missing indexing before retrieval
- Integrated `enhance_chunks()` into the ingestion pipeline
- Eliminated stale vector retrieval issue

### Technical Debt
- Improve numeric/table extraction
- Improve retrieval quality
- Better collection lifecycle management
- Evaluation metrics