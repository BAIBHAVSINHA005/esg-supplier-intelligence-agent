from app.agent.nodes.ingest import ingest_document

test_state = {
    "source_filename": "test_brsr.pdf"
}

result = ingest_document(test_state)

print(result)