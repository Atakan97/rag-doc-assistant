"""
Data source configuration for documentation ingestion.

"""

SOURCES = {
    "fastapi": {
        "repo_url": "https://github.com/fastapi/fastapi.git",
        "branch": "master",
        # Glob patterns relative to the repo root
        "include_patterns": [
            "docs/en/docs/**/*.md",
        ],
        # Base URL for constructing GitHub links to source files
        "github_blob_base": "https://github.com/fastapi/fastapi/blob/master",
    },
}


def build_source_url(collection: str, relative_path: str) -> str:
    """
    Build a GitHub blob URL for a given file path.
    """
    base = SOURCES[collection]["github_blob_base"]
    # Ensure forward slashes for URLs regardless of OS
    clean_path = relative_path.replace("\\", "/")
    return f"{base}/{clean_path}"
