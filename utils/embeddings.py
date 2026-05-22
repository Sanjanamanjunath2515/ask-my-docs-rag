"""
Local embeddings using sentence-transformers (all-MiniLM-L6-v2).

The SentenceTransformer is loaded via app.py @st.cache_resource — never import
Streamlit in this module. Pass the cached model into EmbeddingGenerator.
"""

import hashlib
import json
import logging
import os
from pathlib import Path
from typing import List, Optional

import numpy as np

from utils.text_splitter import TextChunk

logger = logging.getLogger(__name__)

MODEL_NAME = "all-MiniLM-L6-v2"
HF_REPO_ID = f"sentence-transformers/{MODEL_NAME}"
CACHE_DIR = Path("data/embedding_cache")
LOCAL_MODEL_DIR = Path("data/models") / MODEL_NAME


def _configure_ssl_certs() -> None:
    """Fix SSL on Windows using OS cert store (truststore) + certifi fallback."""
    try:
        import truststore

        truststore.inject_into_ssl()
    except ImportError:
        pass

    try:
        import certifi

        ca = certifi.where()
        os.environ.setdefault("SSL_CERT_FILE", ca)
        os.environ.setdefault("REQUESTS_CA_BUNDLE", ca)
    except ImportError:
        pass


def _reset_huggingface_http_client() -> None:
    """
    Recreate huggingface_hub httpx client.

    After SSL errors the hub closes the shared client but retries may reuse it,
    causing: 'Cannot send a request, as the client has been closed.'
    """
    try:
        import httpx
        from huggingface_hub.utils._http import close_session, get_session, set_client_factory

        def _factory() -> httpx.Client:
            verify: bool | str = True
            try:
                import certifi

                verify = certifi.where()
            except ImportError:
                pass
            return httpx.Client(verify=verify, timeout=httpx.Timeout(120.0), follow_redirects=True)

        set_client_factory(_factory)
        close_session()
        get_session()
    except Exception as exc:
        logger.debug("HF HTTP client reset skipped: %s", exc)


def _configure_hf_env(*, offline: bool = False) -> None:
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "0")
    if offline and _local_model_ready():
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"


def _local_model_ready() -> bool:
    if not LOCAL_MODEL_DIR.is_dir():
        return False
    for name in ("modules.json", "config.json", "config_sentence_transformers.json"):
        if (LOCAL_MODEL_DIR / name).exists():
            return True
    return False


def _download_model_snapshot() -> Path:
    from huggingface_hub import snapshot_download

    _configure_ssl_certs()
    _reset_huggingface_http_client()
    _configure_hf_env(offline=False)

    LOCAL_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    path = snapshot_download(repo_id=HF_REPO_ID, local_dir=str(LOCAL_MODEL_DIR))
    return Path(path)


def load_sentence_transformer(model_name: str = MODEL_NAME):
    """
    Load all-MiniLM-L6-v2 once (call from Streamlit @st.cache_resource only).
    """
    _configure_ssl_certs()
    _configure_hf_env(offline=_local_model_ready())

    from sentence_transformers import SentenceTransformer

    if _local_model_ready():
        logger.info("Loading embedding model from %s", LOCAL_MODEL_DIR)
        _reset_huggingface_http_client()
        return SentenceTransformer(str(LOCAL_MODEL_DIR), device="cpu", local_files_only=True)

    last_err: Optional[Exception] = None
    for attempt in range(3):
        try:
            _reset_huggingface_http_client()
            if not _local_model_ready():
                logger.info("Downloading %s (attempt %d)", HF_REPO_ID, attempt + 1)
                _download_model_snapshot()

            model = SentenceTransformer(
                str(LOCAL_MODEL_DIR) if _local_model_ready() else model_name,
                device="cpu",
                local_files_only=_local_model_ready(),
            )
            if not _local_model_ready():
                LOCAL_MODEL_DIR.parent.mkdir(parents=True, exist_ok=True)
                model.save(str(LOCAL_MODEL_DIR))

            _configure_hf_env(offline=True)
            return model
        except RuntimeError as exc:
            last_err = exc
            if "client has been closed" in str(exc).lower():
                _reset_huggingface_http_client()
                continue
            raise
        except Exception as exc:
            last_err = exc
            _reset_huggingface_http_client()
            if attempt == 2:
                raise
    raise RuntimeError(f"Failed to load embedding model '{model_name}'") from last_err


class EmbeddingGenerator:
    """Embed text using a pre-loaded SentenceTransformer (injected from app cache)."""

    def __init__(self, model, *, use_disk_cache: bool = True):
        self._model = model
        self.use_disk_cache = use_disk_cache
        if use_disk_cache:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _cache_key(self, texts: List[str]) -> str:
        return hashlib.sha256(json.dumps(texts, sort_keys=True).encode()).hexdigest()

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.array([]).reshape(0, 384)

        cache_key = None
        if self.use_disk_cache:
            cache_key = self._cache_key(texts)
            path = CACHE_DIR / f"{cache_key}.npy"
            if path.exists():
                cached = np.load(path)
                if cached.shape[0] == len(texts):
                    logger.debug("Disk cache hit for %d texts", len(texts))
                    return cached.astype(np.float32)

        logger.info("Encoding %d text(s)", len(texts))
        embeddings = self._model.encode(
            texts,
            show_progress_bar=False,
            convert_to_numpy=True,
            batch_size=32,
        ).astype(np.float32)

        if self.use_disk_cache and cache_key:
            try:
                np.save(CACHE_DIR / f"{cache_key}.npy", embeddings)
            except Exception:
                pass

        return embeddings

    def embed_chunks(self, chunks: List[TextChunk]) -> np.ndarray:
        return self.embed_texts([c.content for c in chunks])

    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single query string; returns shape (384,) vector."""
        return self.embed_texts([query])[0]
