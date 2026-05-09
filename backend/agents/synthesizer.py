from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.config import settings

# LLM A — Llama 70B (best reasoning)
groq_llm_a = ChatGroq(
    model="llama-3.3-70b-versatile",
    groq_api_key=settings.groq_api_key,
    temperature=0.2,
)

# LLM B — Gemma2 (different architecture = genuine multi-LLM)
groq_llm_b = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=settings.groq_api_key,
    temperature=0.2,
)

answer_prompt = ChatPromptTemplate.from_template("""
You are a research assistant. Answer the question using ONLY the provided context.
If the context does not contain enough information, say "I don't have enough context to answer this."
Always cite which part of the context supports your answer.

Context:
{context}

Question: {query}

Answer:
""")

groq_chain_a = answer_prompt | groq_llm_a | StrOutputParser()
groq_chain_b = answer_prompt | groq_llm_b | StrOutputParser()

def format_context(retrieved_docs: list[dict]) -> str:
    parts = []
    for i, doc in enumerate(retrieved_docs, 1):
        source = doc.get("source", "unknown")
        parts.append(f"[{i}] ({source.upper()}) {doc['text']}")
    return "\n\n".join(parts)

def generate_answers(query: str, retrieved_docs: list[dict]) -> dict:
    context = format_context(retrieved_docs)
    payload = {"query": query, "context": context}

    print("[Synthesizer] Generating with Groq Llama 70B...")
    answer_a = groq_chain_a.invoke(payload)

    print("[Synthesizer] Generating with Groq Gemma2 9B...")
    answer_b = groq_chain_b.invoke(payload)

    return {
        "answer_a": answer_a,
        "answer_b": answer_b,
        "context": context,
    }
