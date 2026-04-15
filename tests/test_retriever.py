"""Retrieval quality tests. Slower — requires the sentence-transformers model."""
import pytest

from src.embeddings import build_corpus
from src.retriever import retrieve


@pytest.fixture(scope="module")
def corpus():
    return build_corpus()


def _top_names(results, n=3):
    return [r.chunk.name for r in results[:n]]


def test_dandruff_query_surfaces_scalp_products(corpus):
    results = retrieve(corpus, "shampoo for dandruff and itchy scalp", k=5, type_filter="product")
    top = _top_names(results)
    assert any("Neem" in name or "Shampoo" in name or "Scalp" in name for name in top), top


def test_dry_face_query_surfaces_moisturiser(corpus):
    results = retrieve(corpus, "my face is dry and I need hydration", k=5, type_filter="product")
    top = _top_names(results, n=5)
    assert any("Moisturising" in name or "Serum" in name for name in top), top


def test_chapped_lips_query_surfaces_lip_product(corpus):
    results = retrieve(corpus, "dry chapped lips need healing", k=5, type_filter="product")
    top = _top_names(results, n=5)
    assert any("Lip" in name for name in top), top


def test_brand_query_returns_brand_chunk(corpus):
    results = retrieve(corpus, "what is Sigiri Ayu's brand philosophy", k=3, type_filter="brand")
    assert len(results) >= 1
    assert all(r.chunk.type == "brand" for r in results)


def test_retrieval_scores_are_sorted_descending(corpus):
    results = retrieve(corpus, "hair care", k=5)
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)
