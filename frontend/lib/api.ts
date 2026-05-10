const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Source {
  text: string;
  source: string;
  rrf_score: number;
  metadata: Record<string, any>;
}

export interface QueryResponse {
  query: string;
  query_type: string;
  final_answer: string;
  winner: string;
  reason: string;
  sources: Source[];
}

export async function queryPipeline(query: string): Promise<QueryResponse> {
  const res = await fetch(`${API_URL}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) throw new Error("Query failed");
  return res.json();
}

export async function getMetrics() {
  const res = await fetch(`${API_URL}/api/metrics`);
  if (!res.ok) throw new Error("Metrics failed");
  return res.json();
}
