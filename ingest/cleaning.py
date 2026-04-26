"""
Markdown cleaning utilities for documentation ingestion.
"""

import re

def remove_frontmatter(text: str) -> str:
    """
    Remove YAML frontmatter enclosed in --- delimiters at the top of a file.
    """
    # Match frontmatter block at the start of the text
    pattern = r"^---\s*\n.*?\n---\s*\n"
    return re.sub(pattern, "", text, count=1, flags=re.DOTALL)


def remove_shortcodes(text: str) -> str:
    """
    Remove Hugo and MkDocs shortcodes that are not useful for embeddings.
    """
    
    text = re.sub(r"\{\{[<%].*?[%>]\}\}", "", text, flags=re.DOTALL)
    return text


def remove_html_tags(text: str) -> str:
    """
    Remove HTML tags from the text while saving the inner content.
    """
    return re.sub(r"<[^>]+>", "", text)


def remove_admonitions(text: str) -> str:
    """
    Remove MkDocs admonition markers.
    """
    return re.sub(r"^[!?]{3}\s+\w+.*$", "", text, flags=re.MULTILINE)


def normalize_whitespace(text: str) -> str:
    """
    Break down multiple blank lines into a single blank line.
    """
    
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_title(text: str, default_name: str = "Untitled") -> str:
    """
    Extract the document title from the first # heading in the text.
    """
    match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    # If header not found, use default_name (usually filename) without extension
    return default_name.rsplit(".", 1)[0].replace("-", " ").replace("_", " ").title()


def clean_markdown(text: str) -> str:
    """
    Apply all cleaning steps to prepare markdown for chunking.

    """
    text = remove_frontmatter(text)
    text = remove_shortcodes(text)
    text = remove_html_tags(text)
    text = remove_admonitions(text)
    text = normalize_whitespace(text)
    return text
