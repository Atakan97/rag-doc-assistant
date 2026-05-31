"""
FastAPI application entry point for the RAG Documentation Assistant.

Serves two endpoints:
- POST /query: Answer questions using the RAG pipeline
- GET /health: Health check for monitoring

Includes CORS middleware, structured logging, and error handling for Groq rate limits and other failures.
"""

import logging
from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.config import settings
from app.infra.logging import setup_logging
from app.infra.metrics import (
    RAG_ERRORS_TOTAL,
    RAG_QUERY_DURATION_SECONDS,
    RAG_QUERY_TOTAL,
    get_model_label,
)
from app.rag.schemas import QueryRequest, QueryResponse, HealthResponse
from app.rag.chain import run_rag_chain
from app.rag.embeddings import get_embeddings

# Initialize logging before anything else
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler for startup and shutdown events.

    Pre-loads the embedding model during startup to avoid cold-start
    delays on the first user query.
    """
    # Startup: pre loading the embedding model
    logger.info("Starting up: pre-loading embedding model...")
    try:
        get_embeddings()
        logger.info("Embedding model pre-loaded successfully")
    except Exception as e:
        logger.error(f"Failed to pre-load embedding model: {e}")

    yield

    # Shutdown: cleanup if needed
    logger.info("Shutting down RAG Documentation Assistant")


# Create the FastAPI application
app = FastAPI(
    title="RAG Documentation Assistant",
    description="A Retrieval-Augmented Generation API that answers questions from FastAPI documentation with source citations.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS to allow requests from the frontend
# Parse comma-separated origins from the config
allowed_origins = [origin.strip() for origin in settings.cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return HealthResponse(ok=True)


@app.get("/metrics", include_in_schema=False)
async def metrics():
    """
    Prometheus scrape endpoint for custom backend metrics.
    """
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Answer a question using the RAG pipeline.

    Retrieves relevant document chunks from the FastAPI documentation,
    generates an answer according to related sources, and returns both
    the answer and structured source references.
    """
    collection = "fastapi"
    llm_provider = settings.llm_provider.lower()
    model = get_model_label(llm_provider, settings.groq_model, settings.ollama_model)
    start = perf_counter()
    status = "success"

    try:
        logger.info(
            f"Query received | "
            f"top_k={request.top_k} | question={request.question[:80]}..."
        )

        # Run the RAG chain to generate an answer
        response = await run_rag_chain(
            question=request.question,
            collection=collection,
            top_k=request.top_k,
        )

        logger.info(f"Query completed | sources={len(response.sources)}")
        return response

    except Exception as e:
        status = "error"
        error_message = str(e).lower()

        # Handle Groq rate limit errors
        if "rate_limit" in error_message or "429" in error_message:
            logger.warning(f"Groq rate limit hit: {e}")
            RAG_ERRORS_TOTAL.labels(
                error_type="rate_limit",
                llm_provider=llm_provider,
                model=model,
            ).inc()
            raise HTTPException(
                status_code=429,
                detail="The AI service is currently rate-limited. Please wait a moment and try again. The free tier allows 30 requests per minute.",
            )

        # Handle other errors
        logger.error(f"Error processing query: {e}", exc_info=True)
        RAG_ERRORS_TOTAL.labels(
            error_type="backend_error",
            llm_provider=llm_provider,
            model=model,
        ).inc()
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your question. Please try again.",
        )
    finally:
        RAG_QUERY_TOTAL.labels(
            collection=collection,
            llm_provider=llm_provider,
            model=model,
            status=status,
        ).inc()
        RAG_QUERY_DURATION_SECONDS.labels(
            collection=collection,
            llm_provider=llm_provider,
            model=model,
            status=status,
        ).observe(perf_counter() - start)
