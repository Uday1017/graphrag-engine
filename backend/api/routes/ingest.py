from fastapi import APIRouter
from api.models import IngestRequest

router = APIRouter()

@router.post("/ingest")
async def ingest(request: IngestRequest):
    import subprocess
    import sys
    subprocess.Popen([
        sys.executable, "scripts/ingest_arxiv.py",
        "--category", request.category,
        "--limit", str(request.limit)
    ])
    return {"status": "ingestion started", "category": request.category, "limit": request.limit}
