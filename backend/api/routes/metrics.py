from fastapi import APIRouter
from db.qdrant_client import get_client
from utils.config import settings

router = APIRouter()

@router.get("/metrics")
async def metrics():
    client = get_client()
    collection = client.get_collection(settings.qdrant_collection)
    return {
        "status": "ok",
        "vectors_count": collection.vectors_count,
        "collection": settings.qdrant_collection,
    }
