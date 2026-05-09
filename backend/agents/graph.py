from typing import TypedDict
from langgraph.graph import StateGraph, END
from agents.classifier import classify_query
from agents.retriever_vector import retrieve_from_vector
from agents.retriever_graph import retrieve_from_graph
from agents.synthesizer import generate_answers
from agents.judge import judge_answers
from rag.rrf import reciprocal_rank_fusion

class GraphState(TypedDict):
    query: str
    query_type: str
    vector_results: list[dict]
    graph_results: list[dict]
    merged_results: list[dict]
    answer_a: str
    answer_b: str
    context: str
    final_answer: str
    winner: str
    reason: str
    sources: list[dict]

def classify_node(state: GraphState) -> GraphState:
    print(f"\n[Graph] Classifying: '{state['query'][:60]}'")
    query_type = classify_query(state["query"])
    print(f"[Graph] Type: {query_type}")
    return {**state, "query_type": query_type}

def retrieve_vector_node(state: GraphState) -> GraphState:
    results = retrieve_from_vector(state["query"])
    return {**state, "vector_results": results}

def retrieve_graph_node(state: GraphState) -> GraphState:
    if state["query_type"] in ("relational", "analytical"):
        results = retrieve_from_graph(state["query"])
    else:
        results = []
    return {**state, "graph_results": results}

def merge_node(state: GraphState) -> GraphState:
    merged = reciprocal_rank_fusion(
        state["vector_results"],
        state["graph_results"],
        top_n=10,
    )
    return {**state, "merged_results": merged, "sources": merged}

def synthesize_node(state: GraphState) -> GraphState:
    result = generate_answers(state["query"], state["merged_results"])
    return {
        **state,
        "answer_a": result["answer_a"],
        "answer_b": result["answer_b"],
        "context": result["context"],
    }

def judge_node(state: GraphState) -> GraphState:
    result = judge_answers(
        state["query"],
        state["context"],
        state["answer_a"],
        state["answer_b"],
    )
    return {
        **state,
        "final_answer": result["final_answer"],
        "winner": result["winner"],
        "reason": result["reason"],
    }

def build_graph():
    g = StateGraph(GraphState)
    g.add_node("classify",        classify_node)
    g.add_node("retrieve_vector", retrieve_vector_node)
    g.add_node("retrieve_graph",  retrieve_graph_node)
    g.add_node("merge",           merge_node)
    g.add_node("synthesize",      synthesize_node)
    g.add_node("judge",           judge_node)

    g.set_entry_point("classify")
    g.add_edge("classify",        "retrieve_vector")
    g.add_edge("retrieve_vector", "retrieve_graph")
    g.add_edge("retrieve_graph",  "merge")
    g.add_edge("merge",           "synthesize")
    g.add_edge("synthesize",      "judge")
    g.add_edge("judge",           END)

    return g.compile()

pipeline = build_graph()

async def run_pipeline(query: str) -> dict:
    initial_state = GraphState(
        query=query,
        query_type="",
        vector_results=[],
        graph_results=[],
        merged_results=[],
        answer_a="",
        answer_b="",
        context="",
        final_answer="",
        winner="",
        reason="",
        sources=[],
    )
    result = pipeline.invoke(initial_state)
    return result
