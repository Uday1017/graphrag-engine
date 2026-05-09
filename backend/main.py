from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.query import router as query_router
from db.qdrant_client import ensure_collection

app = FastAPI(
    title="GraphRAG Multi-LLM Research Engine",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query_router, prefix="/api")

@app.on_event("startup")
async def startup():
    print("Starting GraphRAG Engine...")
    ensure_collection()
    print("Ready.")

@app.get("/health")
def health():
    return {"status": "ok"}
