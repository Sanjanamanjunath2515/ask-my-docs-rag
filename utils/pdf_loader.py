"""
PDF text extraction using PyPDF2 with graceful error handling.
"""

from dataclasses import dataclass
from typing import BinaryIO, List, Optional, Tuple

import PyPDF2


@dataclass
class PageContent:
    """Text content from a single PDF page."""

    text: str
    page_number: int  # 1-based page number for display


@dataclass
class DocumentContent:
    """Extracted content from one PDF file."""

    filename: str
    pages: List[PageContent]
    error: Optional[str] = None

    @property
    def full_text(self) -> str:
        """Concatenate all page text."""
        return "\n\n".join(p.text for p in self.pages if p.text.strip())

    @property
    def is_valid(self) -> bool:
        return self.error is None and bool(self.full_text.strip())


def extract_text_from_pdf(file_obj: BinaryIO, filename: str) -> DocumentContent:
    """
    Extract text from a PDF file object.

    Args:
        file_obj: File-like object (e.g. Streamlit UploadedFile).
        filename: Original filename for metadata.

    Returns:
        DocumentContent with pages or error message.
    """
    try:
        file_obj.seek(0)
        reader = PyPDF2.PdfReader(file_obj)

        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                return DocumentContent(
                    filename=filename,
                    pages=[],
                    error=f"'{filename}' is encrypted and could not be decrypted.",
                )

        if len(reader.pages) == 0:
            return DocumentContent(
                filename=filename,
                pages=[],
                error=f"'{filename}' has no pages.",
            )

        pages: List[PageContent] = []
        for idx, page in enumerate(reader.pages):
            try:
                text = page.extract_text() or ""
            except Exception as page_err:
                text = ""
                # Continue with other pages; log via empty text
                _ = page_err
            pages.append(PageContent(text=text.strip(), page_number=idx + 1))

        if not any(p.text for p in pages):
            return DocumentContent(
                filename=filename,
                pages=pages,
                error=f"'{filename}' contains no extractable text (may be scanned images).",
            )

        return DocumentContent(filename=filename, pages=pages)

    except PyPDF2.errors.PdfReadError as e:
        return DocumentContent(
            filename=filename,
            pages=[],
            error=f"'{filename}' is not a valid PDF: {e}",
        )
    except Exception as e:
        return DocumentContent(
            filename=filename,
            pages=[],
            error=f"Failed to read '{filename}': {e}",
        )


def load_multiple_pdfs(
    uploaded_files: List[Tuple[BinaryIO, str]],
) -> Tuple[List[DocumentContent], List[str]]:
    """
    Load multiple PDF files.

    Returns:
        Tuple of (successful documents, error messages for failed files).
    """
    documents: List[DocumentContent] = []
    errors: List[str] = []

    for file_obj, filename in uploaded_files:
        doc = extract_text_from_pdf(file_obj, filename)
        if doc.is_valid:
            documents.append(doc)
        elif doc.error:
            errors.append(doc.error)

    return documents, errors
