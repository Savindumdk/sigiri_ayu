"""Build and cache embeddings for the Sigiri Ayu corpus."""
from __future__ import annotations

import hashlib
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import List

import numpy as np

from .data_loader import BRAND_FILE, PRODUCTS_FILE, Chunk, load_all_chunks

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CACHE_PATH = PROJECT_ROOT / "data" / "embeddings_cache.pkl"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@dataclass
class EmbeddedCorpus:
    chunks: List[Chunk]
    vectors: np.ndarray  # shape (n_chunks, dim), L2-normalized
    source_hash: str


def _source_hash() -> str:
    h = hashlib.sha256()
    for path in (BRAND_FILE, PRODUCTS_FILE):
        h.update(path.read_bytes())
    return h.hexdigest()[:16]


def _load_model():
    # Lazy import: keeps test / import time fast for non-embedding tests.
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(MODEL_NAME)


def _embed_texts(texts: List[str]) -> np.ndarray:
    model = _load_model()
    vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return np.asarray(vectors, dtype=np.float32)


def embed_query(query: str) -> np.ndarray:
    vectors = _embed_texts([query])
    return vectors[0]


def build_corpus(force_rebuild: bool = False) -> EmbeddedCorpus:
    current_hash = _source_hash()
    if not force_rebuild and CACHE_PATH.exists():
        try:
            with CACHE_PATH.open("rb") as f:
                cached: EmbeddedCorpus = pickle.load(f)
            if cached.source_hash == current_hash:
                return cached
        except Exception:
            pass  # cache corrupted — rebuild

    chunks = load_all_chunks()
    vectors = _embed_texts([c.text for c in chunks])
    corpus = EmbeddedCorpus(chunks=chunks, vectors=vectors, source_hash=current_hash)
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CACHE_PATH.open("wb") as f:
        pickle.dump(corpus, f)
    return corpus
