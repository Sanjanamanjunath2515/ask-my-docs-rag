"""Reliable HTML rendering across Streamlit versions."""

import streamlit as st


def render_html(html: str) -> None:
    """
    Render raw HTML so it displays as UI (not escaped text).

    Prefer st.html(); fall back to st.markdown(..., unsafe_allow_html=True).
    """
    content = (html or "").strip()
    if not content:
        return

    if hasattr(st, "html"):
        st.html(content, unsafe_allow_javascript=False)
    else:
        st.markdown(content, unsafe_allow_html=True)


def render_css(css: str) -> None:
    """Inject global CSS (style block)."""
    block = css.strip()
    if not block.startswith("<style"):
        block = f"<style>{block}</style>"
    render_html(block)
