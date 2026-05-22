"""
Clean and structure model outputs for readable Streamlit display.
"""

import re

# Patterns for empty or broken bullet lines
_EMPTY_BULLET = re.compile(r"^[\s]*[-*•◦▪]\s*\.?\s*$")
_BROKEN_BULLET = re.compile(r"^[\s]*[-*•]\s*[-*•]")
_ONLY_PUNCT = re.compile(r"^[\s\W]+$")


def _normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_chunk_text(text: str) -> str:
    """Normalize retrieved chunk text while preserving line/bullet structure."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.split("\n")]
    return "\n".join(ln for ln in lines if ln).strip()


def format_context_blocks(sources) -> str:
    """
    Numbered, structured context for Gemini.

    Each block: [n] filename | page X | relevance score
    """
    if not sources:
        return "(No excerpts retrieved.)"

    blocks = []
    for src in sources:
        c = src.chunk
        body = clean_chunk_text(c.content)
        if not body:
            continue
        blocks.append(
            f"[{src.rank}] Document: {c.filename} | Page: {c.page_number} | "
            f"Relevance: {src.score:.2f}\n"
            f"Content:\n{body}"
        )

    return "\n\n".join(blocks) if blocks else "(No usable excerpt text.)"


def clean_answer(text: str) -> str:
    """
    Remove empty bullets, fix broken markdown, ensure readable output.
    """
    if not text or not text.strip():
        return text

    text = _normalize_whitespace(text)
    lines = text.split("\n")
    cleaned: list = []

    for line in lines:
        stripped = line.strip()

        if _EMPTY_BULLET.match(stripped):
            continue
        if _BROKEN_BULLET.match(stripped):
            continue
        if _ONLY_PUNCT.match(stripped):
            continue
        # Bullet with only whitespace after marker
        if re.match(r"^[-*•]\s*$", stripped):
            continue

        cleaned.append(line.rstrip())

    result = "\n".join(cleaned)
    result = re.sub(r"\n{3,}", "\n\n", result)

    # Fix bullets that start with "- " but have no content after colon only
    result = re.sub(r"\n\s*[-*•]\s*:\s*\n", "\n", result)

    return result.strip()


def ensure_complete_answer(answer: str, sources) -> str:
    """
    If answer is too short but we have sources, nudge structure.
    Does not invent facts — only improves formatting hint for UI.
    """
    answer = clean_answer(answer)
    if len(answer) > 80:
        return answer
    if not sources:
        return answer
    return answer
