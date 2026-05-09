import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))

import arxiv
import argparse
from rag.chunker import chunk_text
from rag.embedder import embed
from db.qdrant_client import ensure_collection, upsert_chunks
from db.neo4j_client import create_paper_node, create_author_and_link, create_topic_and_link

TOPIC_KEYWORDS = {
    "transformers": ["transformer", "attention", "bert", "gpt"],
    "RAG": ["retrieval augmented", "rag", "retrieval-augmented"],
    "diffusion": ["diffusion model", "stable diffusion", "ddpm"],
    "reinforcement learning": ["reinforcement learning", "rl", "reward"],
    "graph neural networks": ["graph neural", "gnn", "graph network"],
    "llm": ["large language model", "llm", "language model"],
    "computer vision": ["image classification", "object detection", "vision"],
    "multimodal": ["multimodal", "vision-language", "clip"],
}

def infer_topics(text: str) -> list[str]:
    text_lower = text.lower()
    return [topic for topic, keywords in TOPIC_KEYWORDS.items()
            if any(kw in text_lower for kw in keywords)]

def ingest(category: str, limit: int):
    ensure_collection()
    print(f"Fetching {limit} papers from arXiv [{category}]...")

    search = arxiv.Search(
        query=f"cat:{category}",
        max_results=limit,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    all_chunks = []
    for i, paper in enumerate(search.results()):
        paper_id = paper.entry_id.split("/")[-1]
        metadata = {
            "paper_id": paper_id,
            "title":    paper.title,
            "authors":  [a.name for a in paper.authors],
            "year":     paper.published.year,
            "url":      paper.entry_id,
        }

        create_paper_node({
            "id":       paper_id,
            "title":    paper.title,
            "abstract": paper.summary[:500],
            "year":     paper.published.year,
            "url":      paper.entry_id,
        })
        for author in paper.authors[:5]:
            create_author_and_link(author.name, paper_id)
        for topic in infer_topics(paper.title + " " + paper.summary):
            create_topic_and_link(topic, paper_id)

        chunks = chunk_text(paper.summary, metadata)
        all_chunks.extend(chunks)

        if len(all_chunks) >= 500:
            texts = [c.text for c in all_chunks]
            vectors = embed(texts)
            upsert_chunks([
                {"text": c.text, "vector": v, "metadata": c.metadata}
                for c, v in zip(all_chunks, vectors)
            ])
            print(f"  Upserted {len(all_chunks)} chunks ({i+1} papers done)")
            all_chunks = []

    if all_chunks:
        texts = [c.text for c in all_chunks]
        vectors = embed(texts)
        upsert_chunks([
            {"text": c.text, "vector": v, "metadata": c.metadata}
            for c, v in zip(all_chunks, vectors)
        ])
        print(f"  Upserted final {len(all_chunks)} chunks")

    print(f"\nDone! {limit} papers ingested into Qdrant + Neo4j.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", default="cs.AI")
    parser.add_argument("--limit", type=int, default=500)
    args = parser.parse_args()
    ingest(args.category, args.limit)
