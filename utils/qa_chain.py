"""
Question answering: FAISS retrieval + grounded Gemini generation with timeouts and logging.
"""

import concurrent.futures
import logging
import os
import time
from dataclasses import dataclass
from typing import List, Optional

import google.generativeai as genai
import requests
from dotenv import load_dotenv

from utils.embeddings import EmbeddingGenerator, _configure_ssl_certs
from utils.prompts import build_qa_prompt
from utils.response_formatter import clean_answer, ensure_complete_answer, format_context_blocks
from utils.retrieval import FINAL_TOP_K, retrieve_relevant_chunks
from utils.vector_store import FAISSVectorStore, SearchResult

load_dotenv()

logger = logging.getLogger(__name__)

UNKNOWN_ANSWER = "I don't know based on these documents."
TOP_K = FINAL_TOP_K
GEMINI_TIMEOUT_SEC = 20
MAX_OUTPUT_TOKENS = 768
GEMINI_MODELS = ("gemini-2.0-flash-lite", "gemini-2.5-flash", "gemini-flash-latest")
GEMINI_REST_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


@dataclass
class QAResponse:
    answer: str
    sources: List[SearchResult]
    question: str
    error: Optional[str] = None


def _get_api_key() -> Optional[str]:
    return os.getenv("GOOGLE_API_KEY")


_GEMINI_CONFIGURED = False


def configure_gemini() -> bool:
    """Configure Gemini SDK with REST transport (avoids gRPC SSL hangs on Windows)."""
    global _GEMINI_CONFIGURED
    api_key = _get_api_key()
    if not api_key or api_key.strip() in ("", "your_api_key_here"):
        return False
    if not _GEMINI_CONFIGURED:
        _configure_ssl_certs()
        genai.configure(api_key=api_key, transport="rest")
        _GEMINI_CONFIGURED = True
    return True


def format_history(messages: List[dict], max_turns: int = 3) -> str:
    if not messages:
        return "No prior conversation."
    recent = messages[-(max_turns * 2) :]
    lines = []
    for msg in recent:
        role = msg.get("role", "user").capitalize()
        content = (msg.get("content") or "")[:500]
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def _extract_gemini_text(data: dict) -> str:
    """Parse text from Gemini REST JSON response."""
    candidates = data.get("candidates") or []
    if not candidates:
        return ""
    content = candidates[0].get("content") or {}
    parts = content.get("parts") or []
    texts = [p.get("text", "") for p in parts if p.get("text")]
    return "".join(texts).strip()


def _call_gemini_rest(prompt: str, model_name: str, timeout_sec: int = GEMINI_TIMEOUT_SEC) -> str:
    """
    Direct Gemini REST API via requests (reliable SSL + hard timeout).
    Avoids gRPC which can hang indefinitely on Windows.
    """
    api_key = _get_api_key()
    if not api_key:
        raise ValueError("Missing GOOGLE_API_KEY")

    url = GEMINI_REST_URL.format(model=model_name)
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": MAX_OUTPUT_TOKENS,
            "temperature": 0.15,
            "topP": 0.9,
        },
    }
    response = requests.post(
        url,
        params={"key": api_key},
        json=payload,
        timeout=timeout_sec,
        headers={"Content-Type": "application/json"},
    )
    if response.status_code >= 400:
        raise RuntimeError(f"HTTP {response.status_code}: {response.text[:300]}")
    return _extract_gemini_text(response.json())


def _call_gemini_sdk(prompt: str, model_name: str, timeout_sec: int = GEMINI_TIMEOUT_SEC) -> str:
    """SDK fallback using REST transport only."""
    configure_gemini()
    model = genai.GenerativeModel(
        model_name,
        generation_config={
            "max_output_tokens": MAX_OUTPUT_TOKENS,
            "temperature": 0.15,
            "top_p": 0.9,
        },
    )

    def _request():
        response = model.generate_content(prompt)
        return (response.text or "").strip()

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(_request)
        try:
            return future.result(timeout=timeout_sec)
        except concurrent.futures.TimeoutError as exc:
            raise TimeoutError(f"Gemini SDK ({model_name}) timed out after {timeout_sec}s") from exc


def _retrieval_fallback(sources: List[SearchResult], gemini_error: Optional[str]) -> str:
    """Structured excerpt summary when Gemini is unavailable."""
    if not sources:
        return UNKNOWN_ANSWER

    parts = ["**Retrieved from your documents** (AI summary unavailable):\n"]
    for src in sources[:3]:
        c = src.chunk
        snippet = clean_answer(c.content[:500]) or c.content[:500]
        parts.append(f"- **[{src.rank}] {c.filename}** (p. {c.page_number}): {snippet}")

    if gemini_error:
        parts.append(f"\n_Note: {gemini_error}_")
    return clean_answer("\n".join(parts))


def _generate_with_gemini(prompt: str) -> tuple[str, Optional[str]]:
    """Try REST HTTP first, then SDK. Returns within ~20s total."""
    last_error = None
    for model_name in GEMINI_MODELS:
        for caller_name, caller in (("REST", _call_gemini_rest), ("SDK", _call_gemini_sdk)):
            try:
                logger.info("[Gemini] %s request → %s", caller_name, model_name)
                t0 = time.perf_counter()
                text = caller(prompt, model_name)
                logger.info("[Gemini] %s response in %.2fs", caller_name, time.perf_counter() - t0)
                if text:
                    return text, None
                last_error = f"Empty response ({caller_name}/{model_name})"
            except Exception as exc:
                last_error = str(exc)
                logger.warning("[Gemini] %s/%s failed: %s", caller_name, model_name, exc)
    return "", last_error


def generate_answer(
    question: str,
    vector_store: FAISSVectorStore,
    embedding_generator: EmbeddingGenerator,
    conversation_history: Optional[List[dict]] = None,
    top_k: int = TOP_K,
) -> QAResponse:
    """
    Full RAG pipeline with stage logging. Never blocks indefinitely.
    """
    t_start = time.perf_counter()
    logger.info("[QA] Question: %s", question[:120])

    if not vector_store.is_ready:
        raise ValueError("Vector store is not built. Process documents first.")

    # --- Stage 1–2: Embed query + FAISS hybrid retrieval ---
    logger.info("[FAISS] Hybrid retrieval (top_%d)...", top_k)
    t0 = time.perf_counter()
    sources = retrieve_relevant_chunks(
        question=question,
        vector_store=vector_store,
        embedding_generator=embedding_generator,
        top_k=top_k,
    )
    logger.info("[FAISS] Final %d chunks in %.2fs", len(sources), time.perf_counter() - t0)

    if not sources:
        logger.info("[QA] No chunks found — returning unknown answer")
        return QAResponse(answer=UNKNOWN_ANSWER, sources=[], question=question)

    context = format_context_blocks(sources)
    logger.info("[Context] Prepared %d chars for Gemini", len(context))
    history = format_history(conversation_history or [])
    prompt = build_qa_prompt(question=question, context=context, history=history)

    # --- Stage 3: Gemini (optional if no API key) ---
    if not configure_gemini():
        logger.warning("[Gemini] API key missing — retrieval-only fallback")
        fallback = (
            "Gemini API is not configured. Here are the most relevant excerpts from your documents. "
            "Please set GOOGLE_API_KEY in .env to enable full answers."
        )
        return QAResponse(
            answer=fallback,
            sources=sources,
            question=question,
            error="missing_api_key",
        )

    answer_text, gemini_error = _generate_with_gemini(prompt)

    if not answer_text:
        logger.error("[Gemini] All models failed: %s", gemini_error)
        answer_text = _retrieval_fallback(sources, gemini_error)
        return QAResponse(
            answer=answer_text,
            sources=sources,
            question=question,
            error=gemini_error,
        )

    answer_text = clean_answer(answer_text)
    answer_text = ensure_complete_answer(answer_text, sources)

    lower = answer_text.lower()
    if ("don't know" in lower or "do not know" in lower) and "based on these documents" not in lower:
        answer_text = UNKNOWN_ANSWER

    logger.info("[QA] Complete in %.2fs", time.perf_counter() - t_start)
    return QAResponse(answer=answer_text, sources=sources, question=question)


def generate_answer_safe(
    question: str,
    vector_store: FAISSVectorStore,
    embedding_generator: EmbeddingGenerator,
    conversation_history: Optional[List[dict]] = None,
) -> QAResponse:
    """Wrapper that never raises — suitable for Streamlit UI."""
    try:
        return generate_answer(
            question=question,
            vector_store=vector_store,
            embedding_generator=embedding_generator,
            conversation_history=conversation_history,
        )
    except Exception as exc:
        logger.exception("[QA] Pipeline failed")
        return QAResponse(
            answer=f"An error occurred while processing your question: {exc}",
            sources=[],
            question=question,
            error=str(exc),
        )
