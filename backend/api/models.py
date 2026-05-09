from pydantic import BaseModel
from typing import Optional

class QueryRequest(BaseModel):
    query: str

class SourceDoc(BaseModel):
    text: str
    source: str
    rrf_score: float
    metadata: dict = {}

class QueryResponse(BaseModel):
    query: str
    query_type: str
    final_answer: str
    winner: str
    reason: str
    sources: list[SourceDoc]

class IngestRequest(BaseModel):
    category: str = "cs.AI"
    limit: int = 100
