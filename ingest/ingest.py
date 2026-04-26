"""
Main ingestion script for the RAG Documentation Assistant.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

from dotenv import load_dotenv
from git import Repo as GitRepo
from sentence_transformers import SentenceTransformer
from supabase import create_client

from sources import SOURCES, build_source_url
from cleaning import clean_markdown, extract_title
from chunking import chunk_document

# Load environment variables from .env file in the project root
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

# Configure logging to show progress
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Directory where repos will be cloned
REPOS_DIR = Path(__file__).parent / "repos"

# Batch size for embedding
EMBED_BATCH_SIZE = 64
INSERT_BATCH_SIZE = 50

class BGEEmbeddings:

    def __init__(self, model_name: str, device: str = "cpu"):
        """Load the SentenceTransformer model."""
        self.model = SentenceTransformer(model_name, device=device)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed a list of texts and return list of float lists."""
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()


def clone_or_update_repo(collection: str) -> Path:
    """
    Clone the documentation repo if not already present, or pull latest changes.
    """
    source = SOURCES[collection]
    repo_dir = REPOS_DIR / collection

    if repo_dir.exists():
        logger.info(f"Repository already cloned at {repo_dir}, pulling latest changes.")
        repo = GitRepo(repo_dir)
        repo.remotes.origin.pull()
    else:
        logger.info(f"Cloning {source['repo_url']} (branch: {source['branch']}).")
        REPOS_DIR.mkdir(parents=True, exist_ok=True)
        GitRepo.clone_from(
            source["repo_url"],
            repo_dir,
            branch=source["branch"],
            depth=1,
        )
        logger.info(f"Clone complete: {repo_dir}")

    return repo_dir


def find_markdown_files(collection: str, repo_dir: Path) -> list[Path]:
    """
    Find all markdown files matching the configured glob patterns for a collection.
    """
    source = SOURCES[collection]
    all_files = []

    for pattern in source["include_patterns"]:
        # Use glob to find files matching each pattern
        matched = list(repo_dir.glob(pattern))
        all_files.extend(matched)
        logger.info(f"  Pattern '{pattern}' matched {len(matched)} files")

    # Remove duplicates and sort for consistent ordering
    unique_files = sorted(set(all_files))
    logger.info(f"Total unique markdown files for '{collection}': {len(unique_files)}")
    return unique_files


def process_file(file_path: Path, collection: str, repo_dir: Path) -> list:
    """
    Process a single markdown file
    """
    try:
        raw_content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        logger.warning(f"  Skipping file with encoding error: {file_path.name}")
        return []

    # Skip very short files
    if len(raw_content.strip()) < 50:
        return []

    # Clean the markdown content
    cleaned = clean_markdown(raw_content)

    # Skip if cleaning removed all meaningful content
    if len(cleaned.strip()) < 30:
        return []

    # Extract the document title from the first heading
    title = extract_title(cleaned, default_name=file_path.stem)

    # Build the relative path
    relative_path = str(file_path.relative_to(repo_dir))
    source_url = build_source_url(collection, relative_path)

    # Determine the repo identifier from the source config
    repo_url = SOURCES[collection]["repo_url"]
    repo_name = repo_url.split("github.com/")[-1].replace(".git", "")

    # Split into chunks
    documents = chunk_document(
        content=cleaned,
        collection=collection,
        source_url=source_url,
        title=title,
        repo=repo_name,
        relative_path=relative_path,
    )

    return documents


def create_embeddings_model() -> BGEEmbeddings:
    """
    Initialize the BGE embedding model.
    """
    model_name = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")
    logger.info(f"Loading embedding model: {model_name}")

    embeddings = BGEEmbeddings(
        model_name=model_name,
        device="cpu",
    )

    logger.info("Embedding model loaded successfully")
    return embeddings


def insert_chunks_to_supabase(documents: list, embeddings_model, dry_run: bool = False):
    """
    Embed all document chunks and insert them into the Supabase chunks table.
    """
    if dry_run:
        logger.info(f"[DRY RUN] Would insert {len(documents)} chunks into Supabase")
        return

    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        logger.error("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment")
        sys.exit(1)

    client = create_client(supabase_url, supabase_key)
    total_inserted = 0

    # Process in batches to avoid memory overload
    for batch_start in range(0, len(documents), EMBED_BATCH_SIZE):
        batch_end = min(batch_start + EMBED_BATCH_SIZE, len(documents))
        batch_docs = documents[batch_start:batch_end]

        # Extract text content for embedding
        texts = [doc.page_content for doc in batch_docs]

        # Generate embeddings for this batch
        logger.info(f"  Embedding batch {batch_start}-{batch_end} ({len(texts)} chunks).")
        batch_embeddings = embeddings_model.embed_documents(texts)

        # Prepare rows for insertion
        rows = []
        for doc, embedding in zip(batch_docs, batch_embeddings):
            rows.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "embedding": embedding,
            })

        # Insert rows into Supabase in smaller batches
        for insert_start in range(0, len(rows), INSERT_BATCH_SIZE):
            insert_end = min(insert_start + INSERT_BATCH_SIZE, len(rows))
            insert_batch = rows[insert_start:insert_end]

            result = client.table("chunks").insert(insert_batch).execute()
            total_inserted += len(insert_batch)

        logger.info(f"  Inserted {total_inserted}/{len(documents)} chunks so far")

    logger.info(f"Finished inserting {total_inserted} chunks into Supabase")


def ingest_collection(collection: str, embeddings_model, dry_run: bool = False):
    """
    Run the full ingestion pipeline for a single documentation collection.
    """
    logger.info(f"{'=' * 60}")
    logger.info(f"Starting ingestion for collection: {collection}")
    logger.info(f"{'=' * 60}")

    # Clone or update the repository
    repo_dir = clone_or_update_repo(collection)

    # Find matching markdown files
    md_files = find_markdown_files(collection, repo_dir)

    if not md_files:
        logger.warning(f"No markdown files found for '{collection}'. Check glob patterns.")
        return

    # Process each file
    all_documents = []
    for file_path in md_files:
        docs = process_file(file_path, collection, repo_dir)
        if docs:
            all_documents.extend(docs)

    logger.info(f"Total chunks created for '{collection}': {len(all_documents)}")

    if not all_documents:
        logger.warning(f"No chunks created for '{collection}'. Files may be too short.")
        return

    # Embed and insert into Supabase
    insert_chunks_to_supabase(all_documents, embeddings_model, dry_run=dry_run)

    logger.info(f"Ingestion complete for '{collection}'")


def main():
    """
    Parse command line arguments and run the ingestion pipeline.
    """
    parser = argparse.ArgumentParser(
        description="Ingest documentation into Supabase for RAG retrieval"
    )
    parser.add_argument(
        "--collection",
        choices=list(SOURCES.keys()),
        help="Ingest only a specific collection (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the pipeline without writing to the database",
    )
    args = parser.parse_args()

    # Initialize the embedding model
    embeddings_model = create_embeddings_model()

    # Determine which collections to process
    if args.collection:
        collections = [args.collection]
    else:
        collections = list(SOURCES.keys())

    # Run ingestion for each collection
    for collection in collections:
        ingest_collection(collection, embeddings_model, dry_run=args.dry_run)

    logger.info("All ingestion tasks completed successfully.")


if __name__ == "__main__":
    main()
