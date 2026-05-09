from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from db.neo4j_client import run_query
from utils.config import settings
import re

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=settings.groq_api_key,
    temperature=0,
)

cypher_prompt = ChatPromptTemplate.from_template("""
You are a Neo4j Cypher expert. Generate a Cypher query for the question.

Schema:
- (Paper) props: id, title, abstract, year, url
- (Author) props: name
- (Topic) props: name
- (Author)-[:WROTE]->(Paper)
- (Paper)-[:BELONGS_TO]->(Topic)

Rules:
- LIMIT 10 always
- Output ONLY the Cypher query, no markdown, no explanation

Question: {query}
""")

chain = cypher_prompt | llm | StrOutputParser()

def retrieve_from_graph(query: str) -> list[dict]:
    try:
        cypher = chain.invoke({"query": query}).strip()
        cypher = re.sub(r"```(?:cypher)?|```", "", cypher).strip()
        print(f"[GraphRetriever] Cypher: {cypher}")
        records = run_query(cypher)
        results = []
        for record in records:
            text = " | ".join(f"{k}: {v}" for k, v in record.items())
            results.append({
                "text": text,
                "metadata": record,
                "score": 1.0,
                "source": "graph",
            })
        print(f"[GraphRetriever] Retrieved {len(results)} records")
        return results
    except Exception as e:
        print(f"[GraphRetriever] Error: {e}")
        return []
