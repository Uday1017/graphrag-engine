from fastapi import APIRouter
from api.models import QueryRequest, QueryResponse, SourceDoc
from agents.graph import run_pipeline

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    result = await run_pipeline(request.query)
    sources = [
        SourceDoc(
            text=doc["text"][:300],
            source=doc.get("source", "vector"),
            rrf_score=doc.get("rrf_score", 0.0),
            metadata=doc.get("metadata", {}),
        )
        for doc in result.get("sources", [])
    ]
    return QueryResponse(
        query=result["query"],
        query_type=result["query_type"],
        final_answer=result["final_answer"],
        winner=result["winner"],
        reason=result["reason"],
        sources=sources,
    )
