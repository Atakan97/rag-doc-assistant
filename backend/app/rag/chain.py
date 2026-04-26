"""
LangChain RAG chain that connects retrieval, prompting, and generation together.
Uses LangChain Expression Language to build a pipeline:
1. Retrieve relevant document chunks from Supabase
2. Format them as context for the prompt
3. Generate an answer using the LLM
4. Return the answer along with structured source references
"""

import logging
from langchain_core.output_parsers import StrOutputParser

from app.rag.retriever import retrieve_documents
from app.rag.prompts import get_rag_prompt, format_documents_as_context
from app.rag.llm import get_llm
from app.rag.schemas import QueryResponse

logger = logging.getLogger(__name__)


async def run_rag_chain(
    question: str,
    collection: str,
    top_k: int = 6,
) -> QueryResponse:
    """
    Run the full RAG pipeline for a user question.

    This is the main entry point called by the /query endpoint.
    It operates retrieval, prompt construction, and LLM generation.

    Steps:
    1. Retrieve relevant chunks from Supabase via similarity search
    2. Format retrieved documents as context for the prompt
    3. Build the prompt with system rules + context + question
    4. Call the LLM to generate a grounded answer
    5. Package the answer and sources into a QueryResponse
    """
    logger.info(f"Running RAG chain | collection={collection} | top_k={top_k}")

    # Retrieve relevant documents and source data
    documents, source_items = retrieve_documents(
        question=question, # The user's question
        collection=collection, # Which doc collection to search (FastAPI)
        top_k=top_k, # Number of chunks to retrieve for context
    )

    # Handle case where no relevant documents are found
    if not documents:
        logger.warning("No documents retrieved from Supabase")
        return QueryResponse(
            answer="I don't know based on the provided documentation. No relevant documents were found for your question.",
            sources=[],
        )

    # Format documents into a context string for the prompt
    context = format_documents_as_context(documents)

    # Build the prompt using LangChain prompt template
    prompt = get_rag_prompt()

    # Create and invoke the LangChain Expression Language chain
    llm = get_llm()
    chain = prompt | llm | StrOutputParser()

    # Invoke the chain with context and question
    answer = await chain.ainvoke({
        "context": context,
        "question": question,
    })

    logger.info(f"RAG chain completed | answer length={len(answer)} chars")

    # Return the structured response
    return QueryResponse(
        answer=answer,
        sources=source_items,
    )
