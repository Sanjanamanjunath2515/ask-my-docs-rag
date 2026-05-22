"""
Text chunking with LangChain RecursiveCharacterTextSplitter.
"""

from dataclasses import dataclass
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from utils.pdf_loader import DocumentContent


@dataclass
class TextChunk:
    """A chunk of text with source metadata for citations."""

    content: str
    filename: str
    page_number: int  # Best-effort page attribution
    chunk_index: int


def create_text_splitter(
    chunk_size: int = 900,
    chunk_overlap: int = 150,
) -> RecursiveCharacterTextSplitter:
    """
    Create splitter targeting ~700-1000 character chunks with overlap.

    Default chunk_size=900 sits in the required range.
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        # Extra separators help split resume/project bullet sections cleanly
        separators=["\n\n", "\n•", "\n-", "\n*", "\n", ". ", "; ", " ", ""],
    )


def _page_offsets(pages: List) -> List[tuple]:
    """Build (start_char, end_char, page_number) ranges from page texts."""
    offsets = []
    pos = 0
    for page in pages:
        text = page.text
        start = pos
        end = pos + len(text)
        offsets.append((start, end, page.page_number))
        pos = end + 2  # account for "\n\n" join between pages
    return offsets


def _page_for_position(offsets: List[tuple], position: int) -> int:
    """Map character position to page number."""
    for start, end, page_num in offsets:
        if start <= position < end:
            return page_num
    if offsets:
        return offsets[-1][2]
    return 1


def split_documents(
    documents: List[DocumentContent],
    chunk_size: int = 900,
    chunk_overlap: int = 150,
) -> List[TextChunk]:
    """
    Split multiple documents into chunks with filename and page metadata.
    """
    splitter = create_text_splitter(chunk_size, chunk_overlap)
    all_chunks: List[TextChunk] = []
    global_index = 0

    for doc in documents:
        full_text = doc.full_text
        if not full_text.strip():
            continue

        offsets = _page_offsets(doc.pages)
        splits = splitter.split_text(full_text)

        search_start = 0
        for split_text in splits:
            # Find approximate position in full text for page attribution
            pos = full_text.find(split_text[: min(80, len(split_text))], search_start)
            if pos == -1:
                pos = search_start
            page_num = _page_for_position(offsets, pos)
            search_start = pos + len(split_text) // 2

            all_chunks.append(
                TextChunk(
                    content=split_text,
                    filename=doc.filename,
                    page_number=page_num,
                    chunk_index=global_index,
                )
            )
            global_index += 1

    return all_chunks
