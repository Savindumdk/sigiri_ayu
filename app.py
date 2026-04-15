"""Sigiri Ayu RAG Chatbot — Streamlit entry point."""
from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from src.chat_flow import (
    CATEGORY_OPTIONS,
    FlowState,
    Stage,
    build_recommendation_query,
    concerns_for,
    next_stage,
    types_for,
)
from src.embeddings import build_corpus
from src.rag_chain import StreamingRagSession
from src.ui import (
    bubble_text_for_stage,
    inject_css,
    render_header,
    render_mascot,
    render_product_cards,
    render_question_label,
)

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")


st.set_page_config(
    page_title="Sigiri Ayu Assistant",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed",
)

ASSISTANT_AVATAR = "🌿"
USER_AVATAR = "🧖‍♀️"


@st.cache_resource(show_spinner="Warming up the herbal garden...")
def get_corpus():
    return build_corpus()


def _get_api_key() -> str | None:
    env_key = os.getenv("GEMINI_API_KEY")
    if env_key:
        return env_key
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None


def _init_state() -> None:
    if "flow" not in st.session_state:
        st.session_state.flow = FlowState()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "bubble" not in st.session_state:
        st.session_state.bubble = bubble_text_for_stage("start")
    if "pending_query" not in st.session_state:
        st.session_state.pending_query = None  # tuple (query, mode) or None


def _append_message(role: str, content: str, products: list[str] | None = None) -> None:
    st.session_state.messages.append(
        {"role": role, "content": content, "products": products or []}
    )


def _render_history() -> None:
    for msg in st.session_state.messages:
        avatar = ASSISTANT_AVATAR if msg["role"] == "assistant" else USER_AVATAR
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("products"):
                render_product_cards(msg["products"])


def _stream_assistant_response(query: str, mode: str) -> None:
    """Stream Gemini response into a chat_message bubble using st.write_stream."""
    api_key = _get_api_key()
    if not api_key:
        with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
            st.markdown(
                "I'm missing my Gemini API key. Please set GEMINI_API_KEY in your "
                ".env file or Streamlit secrets."
            )
        _append_message("assistant", "Missing GEMINI_API_KEY")
        st.session_state.bubble = bubble_text_for_stage("free_chat")
        return

    corpus = get_corpus()
    session = StreamingRagSession(
        query=query,
        corpus=corpus,
        history=st.session_state.messages,
        mode=mode,
        api_key=api_key,
    )

    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
        try:
            full_text = st.write_stream(session.stream())
        except Exception as e:
            full_text = f"Sorry, I ran into an issue: {e}"
            st.markdown(full_text)
            _append_message("assistant", full_text)
            st.session_state.bubble = bubble_text_for_stage("free_chat")
            return

        products = session.products
        if not products and mode == "recommend":
            products = session.retrieved_names[:3]
        if products:
            render_product_cards(products)

    _append_message("assistant", full_text, products=products)
    st.session_state.bubble = (
        bubble_text_for_stage("recommend")
        if mode == "recommend"
        else bubble_text_for_stage("free_chat")
    )


def _render_questionnaire() -> None:
    flow: FlowState = st.session_state.flow

    if flow.stage == Stage.START:
        st.session_state.bubble = bubble_text_for_stage("start")
        render_question_label("I'll ask 3 quick questions to find your perfect ritual 🌿")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✨ Get a recommendation", key="start_rec"):
                flow.stage = Stage.ASK_CATEGORY
                st.rerun()
        with col2:
            if st.button("💬 Just chat", key="start_chat"):
                flow.stage = Stage.FREE_CHAT
                st.session_state.bubble = bubble_text_for_stage("free_chat")
                st.rerun()
        return

    if flow.stage == Stage.ASK_CATEGORY:
        st.session_state.bubble = bubble_text_for_stage("ask_category")
        render_question_label("What area would you like to focus on?")
        cols = st.columns(2)
        for i, opt in enumerate(CATEGORY_OPTIONS):
            with cols[i % 2]:
                if st.button(opt, key=f"cat_{i}"):
                    next_stage(flow, opt)
                    _append_message("user", f"I'm looking for {opt}")
                    st.rerun()
        return

    if flow.stage == Stage.ASK_CONCERN:
        st.session_state.bubble = bubble_text_for_stage("ask_concern")
        category = flow.answers.get("category", "")
        render_question_label(f"What's your main concern in {category}?")
        options = concerns_for(category)
        cols = st.columns(2)
        for i, opt in enumerate(options):
            with cols[i % 2]:
                if st.button(opt, key=f"con_{i}"):
                    next_stage(flow, opt)
                    _append_message("user", f"My main concern is {opt}")
                    st.rerun()
        return

    if flow.stage == Stage.ASK_TYPE:
        st.session_state.bubble = bubble_text_for_stage("ask_type")
        category = flow.answers.get("category", "")
        render_question_label("How would you describe your skin / scalp type?")
        options = types_for(category)
        cols = st.columns(2)
        for i, opt in enumerate(options):
            with cols[i % 2]:
                if st.button(opt, key=f"typ_{i}"):
                    next_stage(flow, opt)
                    _append_message("user", f"My type is {opt}")
                    query = build_recommendation_query(flow.answers)
                    st.session_state.pending_query = (query, "recommend")
                    flow.stage = Stage.FREE_CHAT
                    st.session_state.bubble = bubble_text_for_stage("thinking")
                    st.rerun()
        return


def main() -> None:
    inject_css()
    render_header()
    _init_state()

    flow: FlowState = st.session_state.flow

    render_mascot(st.session_state.bubble)
    _render_history()

    pending = st.session_state.pending_query
    if pending:
        query, mode = pending
        st.session_state.pending_query = None
        st.session_state.bubble = bubble_text_for_stage("thinking")
        _stream_assistant_response(query, mode)

    if flow.stage in (Stage.START, Stage.ASK_CATEGORY, Stage.ASK_CONCERN, Stage.ASK_TYPE):
        _render_questionnaire()
    else:
        user_query = st.chat_input("Ask about products, ingredients, or the brand...")
        if user_query:
            _append_message("user", user_query)
            st.session_state.pending_query = (user_query, "chat")
            st.session_state.bubble = bubble_text_for_stage("thinking")
            st.rerun()


if __name__ == "__main__":
    main()
