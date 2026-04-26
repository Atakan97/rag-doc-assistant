"""
Pydantic models for API request and response validation. 
Defines the data contracts between frontend and backend.
"""

from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    """
    Incoming request body for the /query endpoint.
    The frontend sends a user question along with the selected documentation collection to search.
    """
    question: str = Field(
        ...,
        description="The user's question about the documentation",
        min_length=1,
        max_length=1000,
    )
    collection: str = Field(
        default="fastapi",
        description="Documentation collection to search",
    )
    top_k: int = Field(
        default=6,
        description="Number of relevant chunks to retrieve",
        ge=1,
        le=20,
    )

class SourceItem(BaseModel):
    """
    A single source reference returned with the RAG answer.

    Contains enough information for the frontend to display a source.
    """

    title: str = Field(
        description="Title of the source document"
    )
    source_url: str = Field(
        description="Clickable GitHub URL to the original markdown file"
    )
    section: str = Field(
        default="",
        description="Section within the document"
    )
    similarity: float = Field(
        description="Cosine similarity score between 0 and 1"
    )
    snippet: str = Field(
        description="Preview of the chunk content (300-400 characters)"
    )


class QueryResponse(BaseModel):
    """
    Response body from the /query endpoint.

    Contains the LLM-generated answer grounded in source documents,
    plus structured source references for the UI.
    """

    answer: str = Field(
        description="The assistant's answer based on retrieved documentation"
    )
    sources: list[SourceItem] = Field(
        default_factory=list,
        description="List of source documents used to generate the answer"
    )


class HealthResponse(BaseModel):
    """Response body for the /health endpoint."""
    ok: bool = True
