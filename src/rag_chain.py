"""RAG chain: prompt assembly + Gemini generation."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional

from .data_loader import get_product_names
from .embeddings import EmbeddedCorpus
from .retriever import retrieve_mixed, retrieve

SYSTEM_PROMPT = """You are the Sigiri Ayu Assistant — a warm, knowledgeable guide for the Sigiri Ayu Ayurvedic beauty brand. You feel like a thoughtful friend who happens to know a lot about plant-based skincare.

RULES:
1. Answer ONLY using information from the CONTEXT section below.
2. If the question isn't covered by the context, politely say so and gently steer the conversation back to Sigiri Ayu products or the brand.
3. When recommending, suggest 2-3 specific products and explain WHY each one fits the user's needs (key ingredients, benefits, suitability). Keep each reason to 1-2 sentences.
4. Use a calm, friendly, wellness-oriented tone. Be concise — favor short paragraphs and clear structure. Avoid medical claims.
5. Always use the EXACT product name as written in the context (so images can be matched).
6. Never invent products, ingredients, or claims that are not in the context.
7. After giving a recommendation or detailed answer, end with ONE short, natural follow-up invitation — e.g. "Want me to suggest alternatives?", "Curious about how to use it?", or "Looking for something else too?". Keep it light, conversational, and never pushy.
"""


@dataclass
class RagAnswer:
    text: str
    product_matches: List[str]
    retrieved_names: List[str]


def _format_history(history: List[dict], max_turns: int = 6) -> str:
    if not history:
        return ""
    recent = history[-(max_turns * 2):]
    lines = []
    for msg in recent:
        role = "User" if msg["role"] == "user" else "Assistant"
        lines.append(f"{role}: {msg['content']}")
    return "\n".join(lines)


def _build_prompt(query: str, context: str, history: str) -> str:
    parts = [SYSTEM_PROMPT, "\nCONTEXT:\n", context]
    if history:
        parts.extend(["\n\nRECENT CONVERSATION:\n", history])
    parts.extend(["\n\nCURRENT USER MESSAGE:\n", query, "\n\nASSISTANT RESPONSE:"])
    return "".join(parts)


def _extract_product_mentions(answer_text: str, known_names: List[str]) -> List[str]:
    mentions: List[str] = []
    lowered = answer_text.lower()
    for name in known_names:
        if name.lower() in lowered and name not in mentions:
            mentions.append(name)
    return mentions


def _call_gemini(prompt: str, api_key: Optional[str] = None) -> str:
    import google.generativeai as genai

    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not set. Add it to your .env file.")
    genai.configure(api_key=key)
    model = genai.GenerativeModel(
        "gemini-flash-latest",
        generation_config={"temperature": 0.3, "max_output_tokens": 2048},
    )
    response = model.generate_content(prompt)
    return (response.text or "").strip()


def answer(
    query: str,
    corpus: EmbeddedCorpus,
    history: Optional[List[dict]] = None,
    mode: str = "chat",
    api_key: Optional[str] = None,
    generator=None,
) -> RagAnswer:
    """Run the RAG pipeline (non-streaming). `generator` is injectable for tests."""
    if mode == "recommend":
        retrieved = retrieve(corpus, query, k=6, type_filter="product")
    else:
        retrieved = retrieve_mixed(corpus, query, k_products=5, k_brand=2)

    context = "\n\n---\n\n".join(r.chunk.text for r in retrieved)
    history_str = _format_history(history or [])
    prompt = _build_prompt(query, context, history_str)

    gen_fn = generator if generator is not None else _call_gemini
    text = gen_fn(prompt) if generator is not None else gen_fn(prompt, api_key=api_key)

    known_names = get_product_names()
    mentions = _extract_product_mentions(text, known_names)

    return RagAnswer(
        text=text,
        product_matches=mentions,
        retrieved_names=[r.chunk.name for r in retrieved if r.chunk.type == "product"],
    )


class StreamingRagSession:
    """Streaming RAG: yields text deltas as they arrive from Gemini.

    Usage:
        session = StreamingRagSession(query, corpus, history, mode, api_key)
        for delta in session.stream():
            placeholder.markdown(session.full_text)
        # session.full_text, session.products, session.retrieved_names are now populated
    """

    def __init__(
        self,
        query: str,
        corpus: EmbeddedCorpus,
        history: Optional[List[dict]] = None,
        mode: str = "chat",
        api_key: Optional[str] = None,
    ):
        self.query = query
        self.corpus = corpus
        self.history = history or []
        self.mode = mode
        self.api_key = api_key
        self.full_text: str = ""
        self.products: List[str] = []
        self.retrieved_names: List[str] = []

    def stream(self):
        if self.mode == "recommend":
            retrieved = retrieve(self.corpus, self.query, k=6, type_filter="product")
        else:
            retrieved = retrieve_mixed(self.corpus, self.query, k_products=5, k_brand=2)
        self.retrieved_names = [r.chunk.name for r in retrieved if r.chunk.type == "product"]

        context = "\n\n---\n\n".join(r.chunk.text for r in retrieved)
        history_str = _format_history(self.history)
        prompt = _build_prompt(self.query, context, history_str)

        import google.generativeai as genai

        key = self.api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("GEMINI_API_KEY is not set. Add it to your .env file.")
        genai.configure(api_key=key)
        model = genai.GenerativeModel(
            "gemini-flash-latest",
            generation_config={"temperature": 0.3, "max_output_tokens": 2048},
        )
        response = model.generate_content(prompt, stream=True)

        for chunk in response:
            try:
                delta = chunk.text or ""
            except Exception:
                delta = ""
            if delta:
                self.full_text += delta
                yield delta

        known_names = get_product_names()
        self.products = _extract_product_mentions(self.full_text, known_names)
