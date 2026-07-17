from app.agent.state import make_initial_state
from app.agent.nodes.ingest import ingest_document

PDF_PATH = r"D:\Portfolio_projects\esg-supplier-intelligence-agent\data\uploads\BAJAJCON_11072026152101_Exchanges_BRSR.pdf"

with open(PDF_PATH, "rb") as f:
    pdf_bytes = f.read()

state = make_initial_state(
    supplier_name="Bajaj",
    source_filename="test.pdf",
    document_bytes=pdf_bytes
)

result = ingest_document(state)

chunks = result["document_chunks"]

print("Total chunks:", len(chunks))

print("\nFIRST CHUNK\n")
print(chunks[0]["text"][:1500])

print("\nCHUNK LENGTH:", len(chunks[0]["text"]))    