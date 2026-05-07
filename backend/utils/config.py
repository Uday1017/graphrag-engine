from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # LLMs
    groq_api_key: str
    google_api_key: str
    mistral_api_key: str

    # Vector DB
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "research_papers"

    # Neo4j
    neo4j_uri: str
    neo4j_username: str
    neo4j_password: str

    # PostgreSQL
    database_url: str

    # App
    embedding_model: str = "all-MiniLM-L6-v2"
    top_k_retrieval: int = 10

    class Config:
        env_file = ".env"

settings = Settings()
