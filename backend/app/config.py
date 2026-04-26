"""
Application configuration loaded from environment variables.

Uses Pydantic BaseSettings so values can come from .env files,
environment variables, or Hugging Face Spaces secrets.
"""

from pathlib import Path
from pydantic_settings import BaseSettings

# Resolve the project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """
    Configuration for the RAG backend application.
    """

    # --- Supabase connection ---
    supabase_url: str = ""
    supabase_service_role_key: str = ""

    # --- Groq LLM ---
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"

    # --- Embedding model ---
    embed_model: str = "BAAI/bge-small-en-v1.5"

    # --- RAG retrieval ---
    top_k: int = 6

    # --- CORS ---
    # Comma-separated list of allowed origins for the frontend
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3050,http://127.0.0.1:3050"

    # --- LLM provider selection ---
    # "groq" for cloud inference, "ollama" for local inference
    llm_provider: str = "groq"

    # --- Ollama settings for local mode ---
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b-instruct"

    class Config:
        # Load values from .env file in the project root
        env_file = str(_PROJECT_ROOT / ".env")
        extra = "ignore"  # Ignore unknown env vars without errors


# Settings instance used across the application
settings = Settings()

