from app.rag.embeddings import get_embedding

vector = get_embedding("Scope 3 emissions disclosed")

print(f"Vector length: {len(vector)}")
print(f"Type: {type(vector)}")
print(f"First 5 values: {vector[:5]}")