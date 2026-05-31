"""
Prometheus metrics for the RAG backend.
"""

from contextlib import contextmanager
from time import perf_counter

from prometheus_client import Counter, Gauge, Histogram


RAG_QUERY_TOTAL = Counter(
    "rag_query_total",
    "Total number of RAG queries processed by the backend.",
    ["collection", "llm_provider", "model", "status"],
)

RAG_QUERY_DURATION_SECONDS = Histogram(
    "rag_query_duration_seconds",
    "End-to-end duration of RAG query handling.",
    ["collection", "llm_provider", "model", "status"],
    buckets=(0.25, 0.5, 1, 2, 4, 8, 16, 32, 64),
)

RAG_EMBEDDING_DURATION_SECONDS = Histogram(
    "rag_embedding_duration_seconds",
    "Duration of embedding the user query.",
    ["collection"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)

RAG_RETRIEVAL_DURATION_SECONDS = Histogram(
    "rag_retrieval_duration_seconds",
    "Duration of Supabase vector retrieval.",
    ["collection"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
)

RAG_LLM_DURATION_SECONDS = Histogram(
    "rag_llm_duration_seconds",
    "Duration of LLM answer generation.",
    ["llm_provider", "model"],
    buckets=(0.25, 0.5, 1, 2, 4, 8, 16, 32, 64),
)

RAG_TOP_SIMILARITY_SCORE = Gauge(
    "rag_top_similarity_score",
    "Latest top similarity score returned by vector retrieval.",
    ["collection"],
)

RAG_ERRORS_TOTAL = Counter(
    "rag_errors_total",
    "Total number of RAG backend errors.",
    ["error_type", "llm_provider", "model"],
)

"""Return the configured model name for the active LLM provider."""
def get_model_label(llm_provider: str, groq_model: str, ollama_model: str) -> str:
    if llm_provider.lower() == "ollama":
        return ollama_model
    else:
        return groq_model


"""Measure a code block and record the elapsed seconds in a histogram."""
@contextmanager
def observe_duration(histogram: Histogram, **labels):
    start = perf_counter()
    try:
        yield
    finally:
        histogram.labels(**labels).observe(perf_counter() - start)
