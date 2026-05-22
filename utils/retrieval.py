"""
Improved retrieval on top of FAISS + sentence-transformers (no stack change).

Pipeline: multi-query embed → over-fetch → hybrid rerank → dedupe → top-k.
"""

import logging
import re
from typing import List, Set

from utils.embeddings import EmbeddingGenerator
from utils.vector_store import FAISSVectorStore, SearchResult

logger = logging.getLogger(__name__)

# Assessment requires top-5; fetch more candidates then rerank down to 5
RETRIEVE_CANDIDATES = 12
FINAL_TOP_K = 5
MIN_SIMILARITY = 0.20

# Lightweight stopwords for keyword overlap (no extra dependencies)
_STOPWORDS: Set[str] = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "must", "shall", "can", "need", "to", "of",
    "in", "for", "on", "with", "at", "by", "from", "as", "into", "through",
    "during", "before", "after", "above", "below", "between", "under",
    "again", "further", "then", "once", "here", "there", "when", "where",
    "why", "how", "all", "each", "few", "more", "most", "other", "some",
    "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too",
    "very", "just", "and", "but", "or", "if", "because", "until", "while",
    "about", "against", "what", "which", "who", "whom", "this", "that",
    "these", "those", "am", "it", "its", "my", "me", "i", "you", "your",
    "we", "they", "them", "their", "he", "she", "his", "her", "tell", "describe",
}

RESUME_PROJECT_KEYWORDS = (
    "resume", "cv", "curriculum", "experience", "project", "projects",
    "skill", "skills", "education", "internship", "intern", "work",
    "employment", "role", "position", "achievement", "responsibilit",
    "technology", "tech stack", "portfolio", "certification",
)


def _tokenize(text: str) -> Set[str]:
    tokens = set(re.findall(r"[a-z0-9]+", text.lower()))
    return {t for t in tokens if len(t) > 2 and t not in _STOPWORDS}


def _keyword_overlap_score(query_tokens: Set[str], chunk_text: str) -> float:
    if not query_tokens:
        return 0.0
    chunk_tokens = _tokenize(chunk_text)
    if not chunk_tokens:
        return 0.0
    overlap = len(query_tokens & chunk_tokens)
    return overlap / len(query_tokens)


def expand_query(question: str) -> str:
    """
    Expand queries about resumes/projects so embeddings match relevant sections.
    """
    q_lower = question.lower()
    extra_terms: List[str] = []

    if any(kw in q_lower for kw in RESUME_PROJECT_KEYWORDS):
        extra_terms.extend([
            "work experience",
            "projects",
            "technical skills",
            "responsibilities",
            "achievements",
            "technologies used",
            "education",
            "role",
        ])

    if "project" in q_lower:
        extra_terms.extend(["project name", "description", "built", "developed", "implemented"])

    if "skill" in q_lower or "technolog" in q_lower:
        extra_terms.extend(["skills", "tools", "frameworks", "programming languages"])

    if "experience" in q_lower or "work" in q_lower:
        extra_terms.extend(["employment", "company", "duration", "duties"])

    if not extra_terms:
        return question

    return f"{question.strip()} {' '.join(extra_terms)}"


def _hybrid_score(
    semantic: float,
    keyword: float,
    *,
    resume_boost: bool,
) -> float:
    """Combine cosine similarity with lexical overlap."""
    weight_sem, weight_kw = 0.65, 0.35
    if resume_boost:
        weight_kw = 0.45
        weight_sem = 0.55
    return weight_sem * semantic + weight_kw * keyword


def _dedupe_by_content(results: List[SearchResult], max_per_file: int = 3) -> List[SearchResult]:
    """Drop near-duplicate chunks; cap chunks per file for diversity."""
    seen_text: Set[str] = set()
    file_counts: dict = {}
    deduped: List[SearchResult] = []

    for r in results:
        key = re.sub(r"\s+", " ", r.chunk.content.strip().lower()[:200])
        if key in seen_text:
            continue
        fname = r.chunk.filename
        if file_counts.get(fname, 0) >= max_per_file:
            continue
        seen_text.add(key)
        file_counts[fname] = file_counts.get(fname, 0) + 1
        deduped.append(r)

    return deduped


def retrieve_relevant_chunks(
    question: str,
    vector_store: FAISSVectorStore,
    embedding_generator: EmbeddingGenerator,
    top_k: int = FINAL_TOP_K,
) -> List[SearchResult]:
    """
    Multi-query FAISS retrieval with hybrid reranking.
    """
    query_tokens = _tokenize(question)
    expanded = expand_query(question)
    resume_boost = any(kw in question.lower() for kw in RESUME_PROJECT_KEYWORDS)

    queries = [question]
    if expanded != question:
        queries.append(expanded)
        logger.info("[Retrieval] Expanded query for resume/project focus")

    # Collect candidates from each query embedding
    by_index: dict = {}
    for q in queries:
        vec = embedding_generator.embed_query(q)
        hits = vector_store.search(vec, top_k=RETRIEVE_CANDIDATES)
        for hit in hits:
            idx = hit.chunk.chunk_index
            if idx not in by_index or hit.score > by_index[idx].score:
                by_index[idx] = hit

    candidates = list(by_index.values())
    if not candidates:
        return []

    # Hybrid rerank
    reranked: List[tuple] = []
    for hit in candidates:
        if hit.score < MIN_SIMILARITY:
            continue
        kw = _keyword_overlap_score(query_tokens, hit.chunk.content)
        combined = _hybrid_score(hit.score, kw, resume_boost=resume_boost)
        reranked.append((combined, hit))

    reranked.sort(key=lambda x: x[0], reverse=True)

    merged: List[SearchResult] = []
    for rank, (combined, hit) in enumerate(reranked, start=1):
        merged.append(
            SearchResult(
                chunk=hit.chunk,
                score=combined,
                rank=rank,
            )
        )

    merged = _dedupe_by_content(merged)
    final = merged[:top_k]

    # Re-assign ranks 1..k
    for i, r in enumerate(final, start=1):
        r.rank = i

    logger.info(
        "[Retrieval] %d candidates → %d after filter/rerank (top score %.3f)",
        len(candidates),
        len(final),
        final[0].score if final else 0.0,
    )
    return final
