"""Reusable UI components for Ask My Docs."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

from utils.html_render import render_css, render_html
from utils.ui_styles import get_theme_css

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
LOTTIE_PATH = ASSETS_DIR / "uploading.json"


@st.cache_data(show_spinner=False)
def load_lottie_animation() -> Optional[dict]:
    try:
        if LOTTIE_PATH.exists():
            with open(LOTTIE_PATH, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return None


def inject_theme(theme: str) -> None:
    render_css(get_theme_css(theme))


def render_lottie_hero(height: int = 200) -> None:
    """Lottie only — no extra empty wrapper divs."""
    animation = load_lottie_animation()
    if animation is None:
        render_html('<div style="text-align:center;font-size:3rem;opacity:0.6;">📄</div>')
        return
    try:
        from streamlit_lottie import st_lottie

        st_lottie(animation, height=height, key="hero_lottie", speed=0.9)
    except ImportError:
        import streamlit.components.v1 as components

        json_str = json.dumps(animation)
        components.html(
            f"""
            <script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>
            <lottie-player autoplay loop mode="normal"
                style="width:100%;max-width:280px;margin:0 auto;display:block;"
                src="data:application/json,{json_str.replace(chr(39), '%27')}">
            </lottie-player>
            """,
            height=height + 20,
        )


def render_hero_block() -> None:
    tags = "".join(
        f'<span class="hero-tag">{t}</span>'
        for t in ("Resumes", "Research", "Reports", "Legal", "Manuals", "Any PDF")
    )
    render_html(
        f'<div class="hero-wrap">'
        f'<h1 class="hero-title">Ask My Docs</h1>'
        f'<p class="hero-sub">Upload documents, ask questions, and get grounded AI answers instantly. '
        f"Works with any PDF — research, business, legal, academic, and more.</p>"
        f'<div class="hero-tags">{tags}</div></div>'
    )


def render_hero_lottie_column(height: int = 200) -> None:
    """Lottie only — no orphan HTML wrappers (avoids empty boxes)."""
    with st.container(border=True):
        render_lottie_hero(height)


def render_stat_cards(documents: int, chunks: int, indexed: bool, gemini_ok: bool) -> None:
    cards = [
        ("📄", "Documents", str(documents)),
        ("🧩", "Chunks indexed", str(chunks)),
        ("🗄️", "Vector DB", "Ready" if indexed else "Empty"),
        ("✨", "AI model", "Online" if gemini_ok else "Key needed"),
    ]
    cols = st.columns(4, gap="medium")
    for col, (icon, label, value) in zip(cols, cards):
        with col:
            render_html(
                f'<div class="stat-card">'
                f'<div class="stat-icon">{icon}</div>'
                f'<div class="stat-value">{value}</div>'
                f'<div class="stat-label">{label}</div></div>'
            )


def _serialize_sources(sources) -> List[Dict[str, Any]]:
    out = []
    for src in sources or []:
        c = src.chunk
        out.append(
            {
                "filename": c.filename,
                "page_number": c.page_number,
                "score": float(src.score),
                "rank": int(src.rank),
                "content": c.content,
                "chunk_index": c.chunk_index,
            }
        )
    return out


def render_source_cards(sources_data: List[Dict[str, Any]], msg_idx: int) -> None:
    if not sources_data:
        return
    st.markdown("**📎 Sources**")
    for i, src in enumerate(sources_data, 1):
        with st.expander(
            f"Source {src.get('rank', i)} — {src['filename']} (page {src['page_number']})",
            expanded=(i == 1),
        ):
            render_html(
                f'<div class="badge-row">'
                f'<span class="badge">📄 {src["filename"]}</span>'
                f'<span class="badge">p. {src["page_number"]}</span>'
                f'<span class="badge">score {src["score"]:.3f}</span></div>'
            )
            st.code(src["content"][:2000], language="text")


def render_chat_message(msg: Dict[str, Any], msg_idx: int) -> None:
    role = msg["role"]
    avatar = "🧑‍💻" if role == "user" else "🤖"
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg.get("content", ""))
        if role == "assistant" and msg.get("sources_data"):
            render_source_cards(msg["sources_data"], msg_idx)


def make_assistant_message(answer: str, sources) -> Dict[str, Any]:
    return {
        "role": "assistant",
        "content": answer,
        "sources_data": _serialize_sources(sources),
    }


def render_footer() -> None:
    render_html(
        '<div class="app-footer">Built with <strong>Streamlit</strong> + '
        "<strong>LangChain</strong> + <strong>Gemini</strong></div>"
    )


def render_upload_zone_hint() -> None:
    render_html(
        '<div class="upload-zone">'
        "<p><strong>Upload PDFs</strong></p>"
        "<p>Resumes · Papers · Reports · Manuals · Any PDF</p></div>"
    )


def render_sidebar_brand() -> None:
    render_html(
        '<div style="text-align:center;padding:0.4rem 0 0.85rem;">'
        '<span style="font-size:1.4rem;">📚</span>'
        '<div style="font-weight:800;font-size:1.05rem;">Ask My Docs</div>'
        '<div style="font-size:0.78rem;opacity:0.75;">Universal document AI</div></div>'
    )
