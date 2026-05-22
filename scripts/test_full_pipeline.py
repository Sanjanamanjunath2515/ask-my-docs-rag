"""End-to-end pipeline test (no Streamlit UI). Run: python scripts/test_full_pipeline.py"""

import io
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

logging.basicConfig(level=logging.INFO, format="%(message)s")

from utils.embeddings import EmbeddingGenerator, _configure_ssl_certs, load_sentence_transformer
from utils.pdf_loader import DocumentContent, PageContent, load_multiple_pdfs
from utils.qa_chain import configure_gemini, generate_answer_safe
from utils.text_splitter import split_documents
from utils.vector_store import FAISSVectorStore


def make_pdf():
    text = (
        "Ask My Docs is a RAG application using FAISS and sentence-transformers. "
        "The embedding model is all-MiniLM-L6-v2. Users upload PDFs and ask questions. "
        "Google Gemini generates grounded answers from retrieved chunks."
    ) * 5
    doc = DocumentContent(
        filename="test.pdf",
        pages=[PageContent(text=text, page_number=1)],
    )
    return doc


def main():
    _configure_ssl_certs()
    print("=== Load embedding model ===")
    model = load_sentence_transformer()
    gen = EmbeddingGenerator(model)
    print("OK")

    print("=== Build index ===")
    doc = make_pdf()
    chunks = split_documents([doc])
    emb = gen.embed_chunks(chunks)
    store = FAISSVectorStore()
    store.build(emb, chunks)
    print(f"OK: {len(chunks)} chunks")

    print("=== QA (Gemini configured:", configure_gemini(), ") ===")
    resp = generate_answer_safe(
        question="What embedding model does Ask My Docs use?",
        vector_store=store,
        embedding_generator=gen,
    )
    print("Answer:", resp.answer[:300])
    print("Sources:", len(resp.sources))
    print("Error:", resp.error)
    assert len(resp.sources) > 0, "expected sources"
    print("\nAll pipeline tests passed.")


if __name__ == "__main__":
    main()
