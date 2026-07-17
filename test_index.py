from app.rag.retriever import (
    index_chunks,
    retrieve_chunks
)

chunks = [
    {
        "chunk_id": "test_1",
        "text": "Scope 3 emissions disclosed for purchased goods and services",
        "page": 15
    },
    {
        "chunk_id": "test_2",
        "text": "Employee welfare and safety initiatives",
        "page": 22
    }
]

index_chunks(chunks)

results = retrieve_chunks("Scope 3 emissions")

print(results)