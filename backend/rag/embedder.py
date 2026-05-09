from sentence_transformers import SentenceTransformer
from utils.config import settings

_model = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"Loading embedding model: {settings.embedding_model}")
        _model = SentenceTransformer(settings.embedding_model)
    return _model

def embed(texts: list[str]) -> list[list[float]]:
    model = get_model()
    return model.encode(texts, show_progress_bar=False).tolist()

def embed_single(text: str) -> list[float]:
    return embed([text])[0]
