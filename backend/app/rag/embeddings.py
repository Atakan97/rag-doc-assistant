"""
HuggingFace BGE embeddings setup for the RAG pipeline.
Provides a single embedding model instance that is loaded once at app start and shared across all requests.
"""

import logging
from sentence_transformers import SentenceTransformer
from app.config import settings

logger = logging.getLogger(__name__)

# Variable to hold the single embeddings model
_embeddings_model = None


class BGEEmbeddings:
    """
    Provides embed_query and embed_documents methods compatible with the LangChain embeddings interface.
    """

    def __init__(self, model_name: str, device: str = "cpu"):
        """Load the SentenceTransformer model."""
        self.model = SentenceTransformer(model_name, device=device)

    def embed_query(self, text: str) -> list[float]:
        """Embed a single query string and return a list of floats."""
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of document strings and return list of float lists."""
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()


def get_embeddings() -> BGEEmbeddings:
    """
    Get or create the single embedding model instance.
    The model is loaded on first call and cached for following requests.
    Uses BGE-small-en-v1.5 running on CPU with normalized embeddings for cosine similarity.
    """
    global _embeddings_model

    if _embeddings_model is None:
        logger.info(f"Loading embedding model: {settings.embed_model}")

        _embeddings_model = BGEEmbeddings(
            model_name=settings.embed_model,
            device="cpu",
        )

        logger.info("Embedding model loaded successfully")

    return _embeddings_model
