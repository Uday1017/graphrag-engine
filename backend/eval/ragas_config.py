import os
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from utils.config import settings

def get_ragas_llm():
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        groq_api_key=settings.groq_api_key,
        temperature=0,
    )
    return LangchainLLMWrapper(llm)

def get_ragas_embeddings():
    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    return LangchainEmbeddingsWrapper(embeddings)
