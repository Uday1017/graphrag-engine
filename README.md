# GraphRAG Multi-LLM Research Engine

A production-grade question-answering system over research papers. Combines semantic vector search with knowledge graph traversal, orchestrates multiple LLMs to generate answers, and automatically evaluates every response — built entirely on free-tier infrastructure.

**Live demo** → [graphrag-engine.vercel.app](https://graphrag-engine.vercel.app) &nbsp;|&nbsp; **API docs** → [graphrag-engine.railway.app/docs](https://graphrag-engine.railway.app/docs)

---

## What it does

You ask a question. The system:

1. Classifies your query as factual, relational, or analytical
2. Retrieves relevant chunks from a Qdrant vector database (semantic search)
3. Simultaneously queries a Neo4j knowledge graph (relational traversal)
4. Merges both result sets using Reciprocal Rank Fusion
5. Sends the merged context to two LLMs — Groq Llama 3.3 70B and Llama 3.1 8B — which each generate an answer independently
6. A judge LLM picks the better answer with explicit reasoning
7. Returns the final answer with source attribution and eval scores

---

## Architecture

```
User query
    │
    ▼
Classifier (Llama 3.1 8B)
    │
    ├─────────────────────┐
    ▼                     ▼
Qdrant retrieval      Neo4j Cypher traversal
(semantic search)     (relational facts)
    │                     │
    └──────────┬───────────┘
               ▼
        RRF merge
               │
    ┌──────────┴──────────┐
    ▼                     ▼
Groq Llama 70B        Groq Llama 8B
(Answer A)            (Answer B)
    │                     │
    └──────────┬───────────┘
               ▼
          Judge LLM
               │
               ▼
    Final answer + sources + eval score
```

---

## Tech stack

| Layer | Tool | Purpose |
|-------|------|---------|
| Orchestration | LangGraph | Stateful multi-agent pipeline |
| LLM routing | LangChain | Prompt management, chain composition |
| LLM A | Groq (Llama 3.3 70B) | Primary reasoning |
| LLM B | Groq (Llama 3.1 8B) | Secondary answer + classifier + judge |
| Vector DB | Qdrant | Semantic similarity search |
| Graph DB | Neo4j AuraDB | Relational knowledge traversal |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Local, zero cost |
| Evaluation | Custom LLM-as-judge | Faithfulness + relevancy scoring |
| Backend | FastAPI | REST API |
| Frontend | Next.js + Tailwind | Query interface |

**Eval results (10 test queries):** 78% faithfulness · 76% answer relevancy

---

## Knowledge graph schema

```
(Author)-[:WROTE]->(Paper)-[:BELONGS_TO]->(Topic)
                       │
                  [:PUBLISHED_IN]
                       │
                    (Venue)
```

Paper nodes carry: `id, title, abstract, year, url`

This enables queries that vector search alone cannot answer — like "find authors who published papers on both RAG and transformers after 2022."

---

## Getting started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker Desktop

### Free API keys needed

| Service | URL | Used for |
|---------|-----|---------|
| Groq | console.groq.com | All LLM inference |
| Neo4j AuraDB | console.neo4j.io | Knowledge graph (free instance) |

### Setup

```bash
# 1. Clone
git clone https://github.com/Uday1017/graphrag-engine
cd graphrag-engine

# 2. Start Qdrant
docker-compose up -d

# 3. Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your API keys

# 4. Ingest papers
cd ..
python scripts/ingest_arxiv.py --category cs.AI --limit 500

# 5. Run the pipeline test
python scripts/test_pipeline.py

# 6. Start backend
cd backend && uvicorn main:app --reload --port 8000

# 7. Frontend (new terminal)
cd frontend && npm install && npm run dev
```

Open `http://localhost:3000`

---

## Environment variables

```env
# Required
GROQ_API_KEY=

# Neo4j AuraDB
NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
NEO4J_USERNAME=
NEO4J_PASSWORD=

# Qdrant (local Docker — no changes needed)
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=research_papers

# App
EMBEDDING_MODEL=all-MiniLM-L6-v2
TOP_K_RETRIEVAL=10
```

---

## Example queries

**Factual** — answered primarily from vector search
```
What is retrieval augmented generation?
How do transformers use attention mechanisms?
```

**Relational** — answered from Neo4j graph traversal
```
Which authors have published papers on large language models?
What topics appear most in recent AI research?
```

**Analytical** — requires multi-step reasoning across both sources
```
What are the main challenges in training large language models?
How do diffusion models compare to GANs for image generation?
```

---

## Project structure

```
graphrag-engine/
├── backend/
│   ├── agents/
│   │   ├── graph.py           # LangGraph state machine
│   │   ├── classifier.py      # Query type classifier
│   │   ├── retriever_vector.py
│   │   ├── retriever_graph.py # Cypher generation + Neo4j
│   │   ├── synthesizer.py     # Dual LLM answer generation
│   │   └── judge.py           # Best answer selection
│   ├── rag/
│   │   ├── embedder.py        # sentence-transformers
│   │   ├── chunker.py
│   │   └── rrf.py             # Reciprocal Rank Fusion
│   ├── db/
│   │   ├── qdrant_client.py
│   │   └── neo4j_client.py
│   ├── eval/
│   │   └── ragas_runner.py    # Custom eval pipeline
│   ├── api/
│   │   └── routes/
│   └── main.py
├── frontend/
│   ├── app/page.tsx
│   └── lib/api.ts
├── scripts/
│   ├── ingest_arxiv.py
│   └── test_pipeline.py
└── docker-compose.yml
```

---

## Evaluation

Every response is scored automatically:

- **Faithfulness** — does the answer stay within the retrieved context? (no hallucination)
- **Answer relevancy** — does the answer actually address what was asked?

Scores are saved to `backend/eval/ragas_scores.json` after each eval run. This lets you track whether prompt or retrieval changes improve or degrade performance over time.

---

## Total cost to run

Zero. Every tool used has a free tier sufficient for development and demo:

- Groq: 14,400 requests/day free
- Neo4j AuraDB: 1 free instance, 200k nodes
- Qdrant: local Docker, unlimited
- sentence-transformers: runs locally
- Railway + Vercel: free tier deployment
