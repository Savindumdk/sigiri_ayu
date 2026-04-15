"""Tests for the guided questionnaire state machine and RAG chain wiring."""
from src.chat_flow import (
    CATEGORY_OPTIONS,
    FlowState,
    Stage,
    build_recommendation_query,
    concerns_for,
    next_stage,
    types_for,
)
from src.rag_chain import answer
from src.embeddings import build_corpus


def test_flow_walks_through_all_stages():
    flow = FlowState()
    assert flow.stage == Stage.START

    next_stage(flow, "")
    assert flow.stage == Stage.ASK_CATEGORY

    next_stage(flow, "Hair Care")
    assert flow.stage == Stage.ASK_CONCERN
    assert flow.answers["category"] == "Hair Care"

    next_stage(flow, "Dandruff")
    assert flow.stage == Stage.ASK_TYPE
    assert flow.answers["concern"] == "Dandruff"

    next_stage(flow, "Oily")
    assert flow.stage == Stage.RECOMMEND
    assert flow.answers["type"] == "Oily"


def test_reset_clears_state():
    flow = FlowState()
    flow.stage = Stage.RECOMMEND
    flow.answers = {"category": "Hair Care", "concern": "Dandruff", "type": "Oily"}
    flow.reset()
    assert flow.stage == Stage.START
    assert flow.answers == {}


def test_concerns_and_types_are_lists():
    for category in CATEGORY_OPTIONS:
        assert isinstance(concerns_for(category), list)
        assert isinstance(types_for(category), list)
        assert len(concerns_for(category)) >= 2


def test_recommendation_query_includes_all_answers():
    answers = {"category": "Face Care", "concern": "Acne / breakouts", "type": "Oily"}
    query = build_recommendation_query(answers)
    assert "Face Care" in query
    assert "acne" in query.lower()
    assert "oily" in query.lower()


def test_rag_chain_with_mock_generator():
    """Verify the RAG chain wiring end-to-end using a fake generator (no API call)."""
    corpus = build_corpus()

    def fake_generator(prompt: str) -> str:
        # The prompt must contain retrieved context from the corpus.
        assert "Sigiri Ayu" in prompt
        return (
            "I'd recommend Sigiri Ayu Herbal Coconut & Hibiscus Shampoo for gentle cleansing "
            "and Sigiri Ayu Neem & Salt Scalp Scrub to exfoliate and reduce flakes."
        )

    result = answer(
        query="Recommend dandruff care",
        corpus=corpus,
        history=[],
        mode="recommend",
        generator=fake_generator,
    )
    assert "Sigiri Ayu Herbal Coconut & Hibiscus Shampoo" in result.product_matches
    assert "Sigiri Ayu Neem & Salt Scalp Scrub" in result.product_matches
    assert len(result.retrieved_names) > 0
