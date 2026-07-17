from app.rag.client import get_client

client = get_client()

print(client.heartbeat())