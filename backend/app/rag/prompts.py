"""
LangChain prompt templates for the RAG pipeline.

Defines the system and human message templates.
The LLM has to only answer from the provided source documents and always cite its sources.
"""

from langchain_core.prompts import ChatPromptTemplate

# System message
SYSTEM_TEMPLATE = """You are a specialist software architect. Your job is to answer questions accurately using ONLY the provided source documents.

STRICT RULES:
1. Answer ONLY using information from the provided source documents below.
2. If the source documents do not contain enough information to answer the question, respond with: "I don't know based on the provided documentation."
3. Do NOT make up information or use knowledge outside of the provided sources.
4. Always include a "Sources" section at the end of your answer listing the document titles and their URLs.
5. Be concise and technically accurate.
6. Use markdown formatting for code blocks, lists, and emphasis where appropriate.
7. When referring to code, use inline code backticks or fenced code blocks.

SOURCE DOCUMENTS:
{context}"""

# Human message with the user's question
HUMAN_TEMPLATE = """{question}"""


def get_rag_prompt() -> ChatPromptTemplate:
    """
    Build the ChatPromptTemplate used by the RAG chain.

    The template has two variables:
    - context: formatted string of retrieved document chunks
    - question: the user's original question
    """
    return ChatPromptTemplate.from_messages([
        ("system", SYSTEM_TEMPLATE),
        ("human", HUMAN_TEMPLATE),
    ])


def format_documents_as_context(documents: list) -> str:
    """
    Format a list of LangChain Documents into a context string for the prompt.

    Each document is formatted with its title, source URL, and content
    so the LLM can reference and cite specific sources.
    """
    if not documents:
        return "No relevant documents found."

    formatted_parts = []
    for i, doc in enumerate(documents, start=1):
        title = doc.metadata.get("title", "Untitled")
        source_url = doc.metadata.get("source_url", "")
        content = doc.page_content

        part = f"[Document {i}]\nTitle: {title}\nURL: {source_url}\nContent:\n{content}"
        formatted_parts.append(part)

    return "\n\n---\n\n".join(formatted_parts)
