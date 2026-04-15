"""Top-k cosine similarity retrieval over the embedded corpus."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import numpy as np

from .data_loader import Chunk
from .embeddings import EmbeddedCorpus, embed_query


@dataclass
class RetrievedChunk:
    chunk: Chunk
    score: float


def retrieve(
    corpus: EmbeddedCorpus,
    query: str,
    k: int = 5,
    type_filter: Optional[str] = None,
) -> List[RetrievedChunk]:
    q_vec = embed_query(query)
    scores = corpus.vectors @ q_vec  # cosine since vectors are normalized

    indices = np.argsort(-scores)
    results: List[RetrievedChunk] = []
    for idx in indices:
        chunk = corpus.chunks[int(idx)]
        if type_filter and chunk.type != type_filter:
            continue
        results.append(RetrievedChunk(chunk=chunk, score=float(scores[int(idx)])))
        if len(results) >= k:
            break
    return results


def retrieve_mixed(
    corpus: EmbeddedCorpus,
    query: str,
    k_products: int = 5,
    k_brand: int = 2,
) -> List[RetrievedChunk]:
    """Retrieve top product chunks plus a couple of brand chunks for general queries."""
    products = retrieve(corpus, query, k=k_products, type_filter="product")
    brand = retrieve(corpus, query, k=k_brand, type_filter="brand")
    return products + brand
