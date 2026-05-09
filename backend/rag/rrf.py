def reciprocal_rank_fusion(
    vector_results: list[dict],
    graph_results: list[dict],
    k: int = 60,
    top_n: int = 10,
) -> list[dict]:
    scores: dict[str, float] = {}
    docs: dict[str, dict] = {}

    def add_results(results: list[dict], source: str):
        for rank, doc in enumerate(results):
            key = doc["text"][:200]
            scores[key] = scores.get(key, 0) + 1 / (rank + k)
            if key not in docs:
                docs[key] = {**doc, "source": source}
            else:
                docs[key]["source"] = "both"

    add_results(vector_results, "vector")
    add_results(graph_results, "graph")

    ranked_keys = sorted(scores, key=lambda x: scores[x], reverse=True)

    merged = []
    for key in ranked_keys[:top_n]:
        doc = docs[key]
        doc["rrf_score"] = round(scores[key], 4)
        merged.append(doc)

    return merged
