"""
Custom retriever that searches Supabase pgvector with RPC.

Embeds the user's query, calls the match_chunks RPC function in Supabase,
and converts the results into LangChain Document objects for the RAG chain.
Also builds structured SourceItem objects for the API response.
"""

import logging
from langchain_core.documents import Document
from supabase import create_client

from app.config import settings
from app.rag.embeddings import get_embeddings
from app.rag.schemas import SourceItem

logger = logging.getLogger(__name__)

# Snippet length for the sources panel preview
SNIPPET_MAX_LENGTH = 400


def _get_supabase_client():
    """
    Create a Supabase client using credentials from the config.
    """
    return create_client(settings.supabase_url, settings.supabase_service_role_key)

def retrieve_documents(
    question: str,
    collection: str,
    top_k: int = None,
) -> tuple[list[Document], list[SourceItem]]:

    # Use configured default if top_k not specified
    k = top_k or settings.top_k

    logger.info(f"Retrieving top-{k} chunks from '{collection}' for question: {question[:80]}...")

    # Embed the user question
    embeddings = get_embeddings()
    query_embedding = embeddings.embed_query(question)

    # Call Supabase RPC for similarity search
    client = _get_supabase_client()
    response = client.rpc(
        "match_chunks",
        {
            "query_embedding": query_embedding,
            "match_count": k,
            "p_collection": collection,
        },
    ).execute()

    results = response.data or []
    logger.info(f"Retrieved {len(results)} chunks from Supabase")

    # Convert results to LangChain Documents and SourceItems
    documents = []
    source_items = []

    for row in results:
        content = row.get("content", "")
        metadata = row.get("metadata", {})
        similarity = row.get("similarity", 0.0)

        # Create a LangChain Document for the RAG chain context
        doc = Document(
            page_content=content,
            metadata={
                **metadata,
                "similarity": similarity,
            },
        )
        documents.append(doc)

        # Create a SourceItem for the structured API response
        snippet = content[:SNIPPET_MAX_LENGTH]
        if len(content) > SNIPPET_MAX_LENGTH:
            snippet += "..."

        source_item = SourceItem(
            title=metadata.get("title", "Untitled"),
            source_url=metadata.get("source_url", ""),
            section=metadata.get("section", ""),
            similarity=round(similarity, 4),
            snippet=snippet,
        )
        source_items.append(source_item)

    return documents, source_items
