from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct
)
from utils.config import settings
import uuid

_client = None

def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=settings.qdrant_url)
    return _client

def ensure_collection(vector_size: int = 384):
    client = get_client()
    existing = [c.name for c in client.get_collections().collections]
    if settings.qdrant_collection not in existing:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        print(f"Created collection: {settings.qdrant_collection}")

def upsert_chunks(chunks: list[dict]):
    client = get_client()
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=chunk["vector"],
            payload={"text": chunk["text"], **chunk["metadata"]},
        )
        for chunk in chunks
    ]
    client.upsert(collection_name=settings.qdrant_collection, points=points)

def search(query_vector: list[float], top_k: int = 10) -> list[dict]:
    client = get_client()
    results = client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    ).points
    return [
        {
            "text": r.payload.get("text", ""),
            "metadata": {k: v for k, v in r.payload.items() if k != "text"},
            "score": r.score,
            "source": "vector",
        }
        for r in results
    ]
