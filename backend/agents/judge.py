from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.config import settings

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=settings.groq_api_key,
    temperature=0,
)

judge_prompt = ChatPromptTemplate.from_template("""
You are a judge evaluating two AI answers. Pick the better one.

Criteria:
1. Faithfulness — grounded in context, no hallucination
2. Completeness — fully answers the question
3. Clarity — well written

Context: {context}
Question: {query}
Answer A: {answer_a}
Answer B: {answer_b}

Respond in EXACTLY this format:
WINNER: A or B
REASON: one sentence
FINAL_ANSWER: copy the winning answer exactly
""")

chain = judge_prompt | llm | StrOutputParser()

def judge_answers(query: str, context: str, answer_a: str, answer_b: str) -> dict:
    try:
        raw = chain.invoke({
            "query": query,
            "context": context[:3000],
            "answer_a": answer_a,
            "answer_b": answer_b,
        })

        lines = raw.strip().split("\n")
        result = {"winner": "A", "reason": "", "final_answer": answer_a}

        for line in lines:
            if line.startswith("WINNER:"):
                result["winner"] = line.replace("WINNER:", "").strip()
            elif line.startswith("REASON:"):
                result["reason"] = line.replace("REASON:", "").strip()
            elif line.startswith("FINAL_ANSWER:"):
                result["final_answer"] = line.replace("FINAL_ANSWER:", "").strip()

        print(f"[Judge] Winner: {result['winner']} | {result['reason']}")
        return result

    except Exception as e:
        print(f"[Judge] Error: {e}. Defaulting to Answer A.")
        return {"winner": "A", "reason": "Judge error", "final_answer": answer_a}
