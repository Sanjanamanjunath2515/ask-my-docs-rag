"""
Ask My Docs — Universal AI Document Assistant (Streamlit UI).
"""

import logging
import sys
from typing import List

from utils.embeddings import _configure_ssl_certs

_configure_ssl_certs()

import streamlit as st
from dotenv import load_dotenv

from utils.embeddings import EmbeddingGenerator, load_sentence_transformer
from utils.pdf_loader import load_multiple_pdfs
from utils.qa_chain import configure_gemini, generate_answer_safe
from utils.text_splitter import split_documents
from utils.ui_components import (
    inject_theme,
    make_assistant_message,
    render_chat_message,
    render_footer,
    render_hero_block,
    render_hero_lottie_column,
    render_sidebar_brand,
    render_stat_cards,
    render_upload_zone_hint,
)
from utils.vector_store import FAISSVectorStore

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("ask_my_docs")

st.set_page_config(
    page_title="Ask My Docs",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource(show_spinner="Loading AI model (one-time)…")
def get_embedding_model():
    return load_sentence_transformer()


@st.cache_resource
def get_embedding_generator() -> EmbeddingGenerator:
    return EmbeddingGenerator(get_embedding_model(), use_disk_cache=True)


def init_session_state() -> None:
    defaults = {
        "vector_store": None,
        "chunks_count": 0,
        "documents_count": 0,
        "processed": False,
        "messages": [],
        "process_errors": [],
        "is_generating": False,
        "theme": "dark",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def render_theme_toggle() -> None:
    with st.sidebar:
        st.markdown("### 🎨 Appearance")
        is_dark = st.session_state.theme == "dark"
        dark = st.toggle("Dark mode", value=is_dark, key="theme_toggle_widget")
        new_theme = "dark" if dark else "light"
        if new_theme != st.session_state.theme:
            st.session_state.theme = new_theme
            st.rerun()


def process_documents(uploaded_files: List) -> None:
    file_pairs = [(f, f.name) for f in uploaded_files]

    with st.status("Processing documents…", expanded=True) as status:
        st.markdown("📄 **Analyzing documents…**")
        documents, errors = load_multiple_pdfs(file_pairs)
        st.session_state.process_errors = errors

        if not documents:
            status.update(label="Processing failed", state="error")
            st.error("No valid PDFs could be processed.")
            return

        st.markdown("✂️ **Splitting into chunks…**")
        chunks = split_documents(documents)
        if not chunks:
            status.update(label="Processing failed", state="error")
            st.error("No text chunks were created.")
            return

        st.markdown("🧠 **Generating embeddings…**")
        embeddings = get_embedding_generator().embed_chunks(chunks)

        st.markdown("🗄️ **Building FAISS index…**")
        store = FAISSVectorStore()
        store.build(embeddings, chunks)
        try:
            store.save()
        except Exception:
            pass

        st.session_state.vector_store = store
        st.session_state.chunks_count = len(chunks)
        st.session_state.documents_count = len(documents)
        st.session_state.processed = True
        st.session_state.messages = []
        st.session_state.is_generating = False

        status.update(label="Indexed successfully", state="complete")

    st.success(f"Indexed **{len(documents)}** document(s) → **{len(chunks)}** chunks.")


def render_sidebar() -> None:
    with st.sidebar:
        render_sidebar_brand()
        render_upload_zone_hint()

        uploaded = st.file_uploader(
            "Drop PDFs here",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )

        if uploaded:
            st.caption(f"**{len(uploaded)}** file(s) selected")

        if st.button(
            "⚡ Process Documents",
            type="primary",
            use_container_width=True,
            disabled=not uploaded,
            key="index_documents_btn",
        ):
            process_documents(uploaded)

        st.divider()
        st.markdown("**System status**")
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Indexed", "Yes" if st.session_state.processed else "No")
        with c2:
            st.metric("Chunks", st.session_state.chunks_count)

        if configure_gemini():
            st.success("Gemini API connected")
        else:
            st.warning("Set `GOOGLE_API_KEY` in Secrets")

        if st.button("🗑️ Clear chat", use_container_width=True, key="clear_chat"):
            st.session_state.messages = []
            st.session_state.is_generating = False

        st.caption("Upload → Index → Chat")


def run_generation() -> None:
    messages = st.session_state.messages
    if not messages or messages[-1]["role"] != "user":
        st.session_state.is_generating = False
        return

    response = generate_answer_safe(
        question=messages[-1]["content"],
        vector_store=st.session_state.vector_store,
        embedding_generator=get_embedding_generator(),
        conversation_history=messages[:-1],
    )
    st.session_state.messages.append(
        make_assistant_message(response.answer, response.sources)
    )
    st.session_state.is_generating = False


def render_chat() -> None:
    st.markdown("### 💬 Document Chat")

    if not st.session_state.processed or st.session_state.vector_store is None:
        st.info("Upload and index documents in the sidebar to start chatting.")
        return

    with st.container(border=True):
        for idx, msg in enumerate(st.session_state.messages):
            render_chat_message(msg, idx)

        if st.session_state.is_generating:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown("_🔍 Searching vector database…_")
                st.markdown("_✨ Generating AI answer…_")
            run_generation()
            st.rerun()

    prompt = st.chat_input(
        "Ask about your documents — papers, reports, resumes, manuals…"
    )
    if prompt and not st.session_state.is_generating:
        text = prompt.strip()
        if not (
            st.session_state.messages
            and st.session_state.messages[-1].get("role") == "user"
            and st.session_state.messages[-1].get("content") == text
        ):
            st.session_state.messages.append({"role": "user", "content": text})
            st.session_state.is_generating = True
            st.rerun()


def main() -> None:
    init_session_state()
    inject_theme(st.session_state.theme)
    render_theme_toggle()

    try:
        get_embedding_generator()
    except Exception as exc:
        st.sidebar.error(f"Embedding model: {exc}")

    render_sidebar()

    hero_left, hero_right = st.columns([1.12, 0.88], gap="medium")
    with hero_left:
        render_hero_block()
    with hero_right:
        render_hero_lottie_column(195)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    render_stat_cards(
        documents=st.session_state.documents_count,
        chunks=st.session_state.chunks_count,
        indexed=st.session_state.processed,
        gemini_ok=configure_gemini(),
    )

    render_chat()
    render_footer()


if __name__ == "__main__":
    main()
