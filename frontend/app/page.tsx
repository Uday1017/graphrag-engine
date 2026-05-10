"use client";

import { useState } from "react";
import { queryPipeline, QueryResponse } from "@/lib/api";

const EXAMPLES = [
  "What is retrieval augmented generation?",
  "Which authors have published papers on transformers?",
  "How do diffusion models compare to GANs for image generation?",
  "What are the latest approaches to reducing hallucination in LLMs?",
];

export default function Home() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [error, setError] = useState("");
  const [showSources, setShowSources] = useState(false);

  async function handleQuery(q?: string) {
    const finalQuery = q || query;
    if (!finalQuery.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    setShowSources(false);
    try {
      const res = await queryPipeline(finalQuery);
      setResult(res);
      if (q) setQuery(q);
    } catch {
      setError("Something went wrong. Make sure the backend is running on port 8000.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ minHeight: "100vh", background: "#0f172a", color: "#e2e8f0", fontFamily: "system-ui, sans-serif" }}>
      
      {/* Header */}
      <div style={{ borderBottom: "1px solid #1e293b", background: "rgba(15,23,42,0.95)", position: "sticky", top: 0, zIndex: 10, backdropFilter: "blur(8px)" }}>
        <div style={{ maxWidth: 900, margin: "0 auto", padding: "16px 24px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: "#4f46e5", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18 }}>
              🧠
            </div>
            <div>
              <div style={{ fontWeight: 600, color: "#fff", fontSize: 15 }}>GraphRAG Engine</div>
              <div style={{ color: "#64748b", fontSize: 12 }}>Multi-LLM Research Assistant</div>
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 16, fontSize: 12, color: "#64748b" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#4ade80" }}></div>
              Groq 70B + 8B
            </div>
            <div>🗄️ Qdrant + Neo4j</div>
          </div>
        </div>
      </div>

      <div style={{ maxWidth: 900, margin: "0 auto", padding: "48px 24px" }}>

        {/* Hero */}
        {!result && !loading && (
          <div style={{ textAlign: "center", marginBottom: 48 }}>
            <div style={{ display: "inline-flex", alignItems: "center", gap: 8, background: "rgba(79,70,229,0.1)", border: "1px solid rgba(79,70,229,0.3)", borderRadius: 999, padding: "6px 16px", fontSize: 12, color: "#818cf8", marginBottom: 24 }}>
              ⚡ GraphRAG — Vector DB + Knowledge Graph + Multi-LLM
            </div>
            <h2 style={{ fontSize: "clamp(28px, 5vw, 44px)", fontWeight: 700, color: "#fff", marginBottom: 16, lineHeight: 1.2 }}>
              Ask anything about<br />
              <span style={{ color: "#818cf8" }}>AI research papers</span>
            </h2>
            <p style={{ color: "#64748b", fontSize: 17, maxWidth: 520, margin: "0 auto" }}>
              Powered by 500+ arXiv papers. Retrieves from Qdrant and Neo4j,
              generates with Llama 70B + 8B, judges the best answer.
            </p>
          </div>
        )}

        {/* Search */}
        <div style={{ display: "flex", gap: 12, marginBottom: 24 }}>
          <div style={{ flex: 1, position: "relative" }}>
            <span style={{ position: "absolute", left: 16, top: "50%", transform: "translateY(-50%)", color: "#64748b", fontSize: 16 }}>🔍</span>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleQuery()}
              placeholder="Ask a research question..."
              style={{
                width: "100%",
                background: "rgba(30,41,59,0.8)",
                border: "1px solid #334155",
                borderRadius: 14,
                padding: "16px 16px 16px 48px",
                color: "#fff",
                fontSize: 15,
                outline: "none",
                boxSizing: "border-box",
              }}
              onFocus={(e) => e.target.style.borderColor = "#4f46e5"}
              onBlur={(e) => e.target.style.borderColor = "#334155"}
            />
          </div>
          <button
            onClick={() => handleQuery()}
            disabled={loading || !query.trim()}
            style={{
              background: loading || !query.trim() ? "#312e81" : "#4f46e5",
              color: "#fff",
              border: "none",
              borderRadius: 14,
              padding: "16px 28px",
              fontWeight: 600,
              fontSize: 15,
              cursor: loading || !query.trim() ? "not-allowed" : "pointer",
              opacity: loading || !query.trim() ? 0.6 : 1,
              whiteSpace: "nowrap",
            }}
          >
            {loading ? "⏳ Thinking..." : "Ask →"}
          </button>
        </div>

        {/* Examples */}
        {!result && !loading && (
          <div style={{ marginBottom: 48 }}>
            <p style={{ textAlign: "center", color: "#475569", fontSize: 12, marginBottom: 12 }}>Try these examples</p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 10 }}>
              {EXAMPLES.map((q) => (
                <button
                  key={q}
                  onClick={() => handleQuery(q)}
                  style={{
                    background: "rgba(30,41,59,0.5)",
                    border: "1px solid #1e293b",
                    borderRadius: 12,
                    padding: "14px 16px",
                    color: "#94a3b8",
                    fontSize: 13,
                    textAlign: "left",
                    cursor: "pointer",
                    transition: "all 0.15s",
                  }}
                  onMouseEnter={(e) => {
                    (e.target as HTMLButtonElement).style.background = "rgba(30,41,59,0.9)";
                    (e.target as HTMLButtonElement).style.borderColor = "#334155";
                    (e.target as HTMLButtonElement).style.color = "#e2e8f0";
                  }}
                  onMouseLeave={(e) => {
                    (e.target as HTMLButtonElement).style.background = "rgba(30,41,59,0.5)";
                    (e.target as HTMLButtonElement).style.borderColor = "#1e293b";
                    (e.target as HTMLButtonElement).style.color = "#94a3b8";
                  }}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div style={{ background: "rgba(30,41,59,0.4)", border: "1px solid #1e293b", borderRadius: 20, padding: 48, textAlign: "center" }}>
            <div style={{ fontSize: 40, marginBottom: 16, animation: "spin 1s linear infinite" }}>⚙️</div>
            <p style={{ color: "#cbd5e1", fontWeight: 500, marginBottom: 8 }}>Running pipeline...</p>
            <div style={{ display: "flex", justifyContent: "center", gap: 16, flexWrap: "wrap", fontSize: 12, color: "#475569", marginTop: 16 }}>
              {["Classifying query", "Retrieving from Qdrant + Neo4j", "Generating with 2 LLMs", "Judge selecting best"].map((step, i) => (
                <span key={i} style={{ display: "flex", alignItems: "center", gap: 4 }}>
                  <span style={{ color: "#4f46e5" }}>→</span> {step}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.2)", borderRadius: 12, padding: 16, color: "#f87171", fontSize: 14 }}>
            {error}
          </div>
        )}

        {/* Result */}
        {result && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

            {/* Badges */}
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              <span style={{ background: "rgba(79,70,229,0.15)", color: "#818cf8", border: "1px solid rgba(79,70,229,0.3)", borderRadius: 999, padding: "4px 14px", fontSize: 12 }}>
                {result.query_type}
              </span>
              <span style={{ background: "rgba(30,41,59,0.8)", color: "#cbd5e1", borderRadius: 999, padding: "4px 14px", fontSize: 12 }}>
                ⚡ Winner: LLM {result.winner}
              </span>
              <span style={{ background: "rgba(30,41,59,0.8)", color: "#64748b", borderRadius: 999, padding: "4px 14px", fontSize: 12 }}>
                🗄️ {result.sources.length} sources retrieved
              </span>
            </div>

            {/* Answer */}
            <div style={{ background: "rgba(30,41,59,0.5)", border: "1px solid #334155", borderRadius: 20, padding: 28 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
                <span style={{ fontSize: 16 }}>🧠</span>
                <span style={{ color: "#818cf8", fontWeight: 600, fontSize: 14 }}>Answer</span>
              </div>
              <p style={{ color: "#e2e8f0", lineHeight: 1.8, fontSize: 15 }}>{result.final_answer}</p>
            </div>

            {/* Judge reasoning */}
            <div style={{ background: "rgba(15,23,42,0.6)", border: "1px solid #1e293b", borderRadius: 14, padding: "14px 20px", display: "flex", gap: 12, alignItems: "flex-start" }}>
              <span style={{ fontSize: 16, flexShrink: 0 }}>⚖️</span>
              <div>
                <div style={{ color: "#475569", fontSize: 11, marginBottom: 4 }}>Judge reasoning</div>
                <p style={{ color: "#94a3b8", fontSize: 13, lineHeight: 1.6 }}>{result.reason}</p>
              </div>
            </div>

            {/* Sources toggle */}
            <button
              onClick={() => setShowSources(!showSources)}
              style={{ display: "flex", alignItems: "center", gap: 8, color: "#64748b", fontSize: 13, background: "none", border: "none", cursor: "pointer", padding: 0 }}
            >
              🗄️ {showSources ? "Hide" : "Show"} retrieved sources ({result.sources.length}) {showSources ? "↑" : "↓"}
            </button>

            {showSources && (
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {result.sources.map((src, i) => (
                  <div key={i} style={{ background: "rgba(30,41,59,0.4)", border: "1px solid #1e293b", borderRadius: 14, padding: 16 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10, flexWrap: "wrap" }}>
                      <span style={{
                        fontSize: 11, padding: "2px 10px", borderRadius: 999,
                        background: src.source === "graph" ? "rgba(74,222,128,0.1)" : src.source === "both" ? "rgba(168,85,247,0.1)" : "rgba(59,130,246,0.1)",
                        color: src.source === "graph" ? "#4ade80" : src.source === "both" ? "#a855f7" : "#60a5fa",
                      }}>
                        {src.source}
                      </span>
                      <span style={{ color: "#475569", fontSize: 11 }}>RRF: {src.rrf_score}</span>
                      {src.metadata?.title && (
                        <span style={{ color: "#64748b", fontSize: 11 }}>{String(src.metadata.title).slice(0, 60)}...</span>
                      )}
                    </div>
                    <p style={{ color: "#94a3b8", fontSize: 13, lineHeight: 1.6 }}>{src.text}</p>
                  </div>
                ))}
              </div>
            )}

            {/* Ask another */}
            <button
              onClick={() => { setResult(null); setQuery(""); }}
              style={{ color: "#818cf8", background: "none", border: "none", cursor: "pointer", fontSize: 14, textAlign: "left", padding: 0 }}
            >
              ← Ask another question
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
