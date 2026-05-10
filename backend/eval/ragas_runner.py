import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from agents.graph import run_pipeline
from utils.config import settings
import asyncio
import json

TEST_QUERIES = [
    "What is retrieval augmented generation?",
    "How do transformers use attention mechanisms?",
    "What are the challenges in training large language models?",
    "How do diffusion models generate images?",
    "What is the role of reinforcement learning in LLMs?",
    "Explain the concept of fine-tuning in deep learning",
    "What are graph neural networks used for?",
    "How does BERT differ from GPT architectures?",
    "What is prompt engineering?",
    "How do multimodal models work?",
]

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=settings.groq_api_key,
    temperature=0,
)

# ── Faithfulness evaluator ────────────────────────────────────────────────────
faithfulness_prompt = ChatPromptTemplate.from_template("""
You are evaluating if an answer is faithful to the given context.
Faithful means: every claim in the answer is supported by the context.
No hallucination, no made-up facts.

Context: {context}
Answer: {answer}

Score from 0.0 to 1.0 where:
1.0 = completely faithful, every claim supported
0.5 = partially faithful, some unsupported claims  
0.0 = not faithful, mostly hallucinated

Respond with ONLY a number like 0.85
""")

# ── Relevancy evaluator ───────────────────────────────────────────────────────
relevancy_prompt = ChatPromptTemplate.from_template("""
You are evaluating if an answer is relevant to the question asked.

Question: {question}
Answer: {answer}

Score from 0.0 to 1.0 where:
1.0 = perfectly answers the question
0.5 = partially answers the question
0.0 = does not answer the question at all

Respond with ONLY a number like 0.85
""")

faith_chain = faithfulness_prompt | llm | StrOutputParser()
rel_chain = relevancy_prompt | llm | StrOutputParser()

def parse_score(text: str) -> float:
    try:
        text = text.strip()
        for word in text.split():
            try:
                score = float(word)
                return min(max(score, 0.0), 1.0)
            except:
                continue
        return 0.5
    except:
        return 0.5

async def collect_results():
    questions, answers, contexts = [], [], []
    print(f"Running {len(TEST_QUERIES)} queries through pipeline...")
    for i, query in enumerate(TEST_QUERIES):
        print(f"\n[{i+1}/{len(TEST_QUERIES)}] {query[:50]}...")
        try:
            result = await run_pipeline(query)
            questions.append(query)
            answers.append(result["final_answer"])
            ctx = " ".join([doc["text"] for doc in result["sources"][:5]])
            contexts.append(ctx)
            print(f"  ✓ Answer: {result['final_answer'][:60]}...")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    return questions, answers, contexts

def evaluate_scores(questions, answers, contexts):
    faith_scores = []
    rel_scores = []

    print(f"\nEvaluating {len(questions)} answers...")
    for i, (q, a, c) in enumerate(zip(questions, answers, contexts)):
        print(f"  [{i+1}/{len(questions)}] Evaluating...")
        try:
            faith_raw = faith_chain.invoke({"context": c[:2000], "answer": a})
            faith = parse_score(faith_raw)
            faith_scores.append(faith)
        except Exception as e:
            print(f"    Faithfulness error: {e}")
            faith_scores.append(0.5)

        try:
            rel_raw = rel_chain.invoke({"question": q, "answer": a})
            rel = parse_score(rel_raw)
            rel_scores.append(rel)
        except Exception as e:
            print(f"    Relevancy error: {e}")
            rel_scores.append(0.5)

        print(f"    Faithfulness: {faith_scores[-1]:.2f} | Relevancy: {rel_scores[-1]:.2f}")

    return faith_scores, rel_scores

def run_eval():
    print("=" * 60)
    print("Custom RAGAS-style Evaluation Pipeline")
    print("=" * 60)

    questions, answers, contexts = asyncio.run(collect_results())
    faith_scores, rel_scores = evaluate_scores(questions, answers, contexts)

    avg_faith = sum(faith_scores) / len(faith_scores)
    avg_rel = sum(rel_scores) / len(rel_scores)

    print("\n" + "=" * 60)
    print("EVALUATION SCORES")
    print("=" * 60)
    print(f"Faithfulness:      {avg_faith:.3f}  ({int(avg_faith*100)}%)")
    print(f"Answer Relevancy:  {avg_rel:.3f}  ({int(avg_rel*100)}%)")
    print(f"Total queries:     {len(questions)}")
    print("=" * 60)

    scores = {
        "faithfulness": round(avg_faith, 3),
        "answer_relevancy": round(avg_rel, 3),
        "total_queries": len(questions),
        "individual": [
            {
                "query": q[:60],
                "faithfulness": f,
                "relevancy": r
            }
            for q, f, r in zip(questions, faith_scores, rel_scores)
        ]
    }

    os.makedirs("backend/eval", exist_ok=True)
    with open("backend/eval/ragas_scores.json", "w") as f:
        json.dump(scores, f, indent=2)

    print(f"\nScores saved to backend/eval/ragas_scores.json")
    print("\n✅ Your resume bullet numbers:")
    print(f"  → {int(avg_faith*100)}% faithfulness score across {len(questions)} test queries")
    print(f"  → {int(avg_rel*100)}% answer relevancy score")

if __name__ == "__main__":
    run_eval()
