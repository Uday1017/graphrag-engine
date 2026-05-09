from rag.embedder import embed_single
from db.qdrant_client import search
from utils.config import settings

def retrieve_from_vector(query: str, top_k: int = None) -> list[dict]:
    k = top_k or settings.top_k_retrieval
    query_vector = embed_single(query)
    results = search(query_vector, top_k=k)
    print(f"[VectorRetriever] Retrieved {len(results)} chunks")
    return results
