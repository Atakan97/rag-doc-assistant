"""
Document chunking using LangChain's RecursiveCharacterTextSplitter.

"""

import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def create_splitter(chunk_size: int = None, chunk_overlap: int = None) -> RecursiveCharacterTextSplitter:
    """
    Create a text splitter configured for markdown documentation.
    """
    # Read configuration from env or use provided values
    size = chunk_size or int(os.getenv("CHUNK_SIZE", "1200"))
    overlap = chunk_overlap or int(os.getenv("CHUNK_OVERLAP", "150"))

    return RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
        length_function=len,
        # Split separators (headers, paragraphs, sentences)
        separators=["\n## ", "\n### ", "\n#### ", "\n\n", "\n", ". ", " ", ""],
    )


def chunk_document(
    content: str,
    collection: str,
    source_url: str,
    title: str,
    repo: str,
    relative_path: str,
    chunk_size: int = None,
    chunk_overlap: int = None,
) -> list[Document]:
    """
    Split a cleaned document into LangChain Document chunks with metadata.
    """
    splitter = create_splitter(chunk_size, chunk_overlap)

    # Split the content into text chunks
    text_chunks = splitter.split_text(content)

    documents = []
    for index, chunk_text in enumerate(text_chunks):
        # Skip empty chunks
        if not chunk_text.strip():
            continue

        # Build metadata for this chunk
        metadata = {
            "collection": collection,
            "source_url": source_url,
            "title": title,
            "section": title,
            "chunk_index": index,
            "repo": repo,
            "path": relative_path,
        }

        # Create a LangChain Document with content and metadata
        doc = Document(page_content=chunk_text, metadata=metadata)
        documents.append(doc)

    return documents
