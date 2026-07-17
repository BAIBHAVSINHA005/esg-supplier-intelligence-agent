from app.agent.state import make_initial_state
from app.agent.nodes.ingest import ingest_document

from app.rag.chunker import enhance_chunks
from app.rag.retriever import (
    index_chunks,
    retrieve_chunks
)

PDF_PATH = r"D:\Portfolio_projects\esg-supplier-intelligence-agent\data\uploads\BAJAJCON_11072026152101_Exchanges_BRSR.pdf"


# --------------------------------------------------
# Read PDF
# --------------------------------------------------

with open(PDF_PATH, "rb") as f:
    pdf_bytes = f.read()

# --------------------------------------------------
# Build initial state
# --------------------------------------------------

state = make_initial_state(
    supplier_name="Bajaj Construction",
    source_filename="BAJAJ_BRSR.pdf",
    document_bytes=pdf_bytes
)

# --------------------------------------------------
# Run ingest node
# --------------------------------------------------

ingest_result = ingest_document(state)

chunks = ingest_result["document_chunks"]

print(f"\nChunks extracted: {len(chunks)}")

# --------------------------------------------------
# Enhance chunks
# --------------------------------------------------

enhanced_chunks = enhance_chunks(chunks)

print(f"Enhanced chunks: {len(enhanced_chunks)}")

# --------------------------------------------------
# Index into Chroma
# --------------------------------------------------

index_chunks(enhanced_chunks)

print("Chunks indexed.")

# --------------------------------------------------
# Test retrieval
# --------------------------------------------------

results = retrieve_chunks(
    "Scope 3 emissions",
    k=5
)

print("\nTOP RESULTS:\n")

for i, doc in enumerate(results["documents"]):
    print(f"Result {i+1}")
    print("-" * 50)
    print(doc[:500])
    print()