from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from utils.config import settings

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=settings.groq_api_key,
    temperature=0,
)

prompt = ChatPromptTemplate.from_template("""
You are a query classifier for a research paper Q&A system.
Classify the query into exactly one of: factual, relational, analytical
Respond with ONLY one word.

- factual: simple definition or summary questions
- relational: questions about connections between authors, papers, topics
- analytical: complex reasoning or comparison questions

Query: {query}
""")

chain = prompt | llm | StrOutputParser()

def classify_query(query: str) -> str:
    try:
        result = chain.invoke({"query": query}).strip().lower()
        for word in ["factual", "relational", "analytical"]:
            if word in result:
                return word
        return "analytical"
    except Exception as e:
        print(f"Classifier error: {e}")
        return "analytical"
