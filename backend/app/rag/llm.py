"""
LLM types for the RAG pipeline.

Supports two providers:
- Groq (default): Cloud-based inference using ChatGroq
- Ollama (optional): Local LLM 

The provider is selected with the LLM_PROVIDER environment variable.
"""

import logging
from langchain_core.language_models import BaseChatModel
from app.config import settings

logger = logging.getLogger(__name__)

# Variable to hold the single LLM instance
_llm_instance: BaseChatModel | None = None


def get_llm() -> BaseChatModel:
    """
    Get or create the single LLM instance based on the configured provider.

    For Groq: Uses ChatGroq with the configured model and API key.
    For Ollama: Uses ChatOllama pointing to the local Ollama server.
    """
    global _llm_instance

    if _llm_instance is not None:
        return _llm_instance

    provider = settings.llm_provider.lower()

    if provider == "groq":
        logger.info(f"Initializing Groq LLM with model: {settings.groq_model}")
        from langchain_groq import ChatGroq

        _llm_instance = ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            temperature=0,       # Output for documentation Q&A
            max_retries=2,       # Retry on transient errors
            max_tokens=1024,     # This is enough for detailed answers with citations
        )

    elif provider == "ollama":
        logger.info(f"Initializing Ollama LLM with model: {settings.ollama_model}")
        from langchain_ollama import ChatOllama

        _llm_instance = ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=0,
        )

    else:
        raise ValueError(
            f"Unsupported LLM provider: '{provider}'. Use 'groq' or 'ollama'."
        )

    logger.info(f"LLM initialized successfully (provider={provider})")
    return _llm_instance
