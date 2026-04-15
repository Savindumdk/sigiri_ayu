"""Streamlit UI helpers: CSS injection, mascot, chat bubbles, product cards."""
from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

import streamlit as st

from .image_matcher import find_image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MASCOT_DIR = PROJECT_ROOT / "Mascot"
MASCOT_IMAGE = MASCOT_DIR / "mascot_image.png"
MASCOT_VIDEO = MASCOT_DIR / "Mascot Animation.webm"


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* ---------- base ---------- */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background:
        radial-gradient(1200px 600px at 80% -10%, rgba(189, 215, 191, 0.35), transparent 55%),
        radial-gradient(1000px 500px at -10% 100%, rgba(232, 224, 187, 0.35), transparent 55%),
        linear-gradient(180deg, #FBFAF4 0%, #F5F3E8 100%) !important;
    font-family: 'Plus Jakarta Sans', -apple-system, 'Segoe UI', Roboto, sans-serif !important;
    color: #1F2937;
}
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stDeployButton"],
[data-testid="stStatusWidget"],
.stDeployButton,
.stAppDeployButton {
    display: none !important;
    visibility: hidden !important;
}

.block-container {
    max-width: 780px;
    padding-top: 1.2rem;
    padding-bottom: 9rem;
}

/* ---------- header ---------- */
.sa-header {
    text-align: center;
    margin: 4px 0 6px 0;
}
.sa-header .logo {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.85rem;
    font-weight: 800;
    background: linear-gradient(135deg, #2E5339 0%, #6B8E5C 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    letter-spacing: -0.6px;
    line-height: 1;
}
.sa-header .tag {
    font-size: 0.78rem;
    color: #6B7563;
    margin-top: 4px;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    font-weight: 500;
}

/* ---------- mascot hero ---------- */
.sa-hero {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 16px 0 10px 0;
    animation: sa-fadein 0.6s ease;
}
.sa-mascot-halo {
    position: relative;
    width: 200px;
    height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background:
        radial-gradient(circle at 50% 50%, rgba(146, 184, 134, 0.35) 0%, rgba(146, 184, 134, 0.10) 45%, transparent 70%);
    animation: sa-float 5s ease-in-out infinite;
}
.sa-mascot-halo::before {
    content: "";
    position: absolute;
    inset: 18px;
    border-radius: 50%;
    background: radial-gradient(circle at 50% 35%, rgba(255,255,255,0.85), rgba(255,255,255,0.25) 60%, transparent 80%);
    z-index: 0;
}
.sa-mascot-halo video, .sa-mascot-halo img {
    position: relative;
    width: 168px;
    height: 168px;
    object-fit: contain;
    z-index: 1;
    filter: drop-shadow(0 8px 16px rgba(46, 83, 57, 0.18));
}
.sa-bubble {
    margin-top: -6px;
    background: linear-gradient(135deg, #2E5339 0%, #4A7C59 100%);
    color: #FFFFFF;
    padding: 10px 18px;
    border-radius: 22px;
    font-size: 0.92rem;
    font-weight: 500;
    max-width: 320px;
    box-shadow: 0 10px 24px rgba(46, 83, 57, 0.22);
    text-align: center;
    position: relative;
}
.sa-bubble::before {
    content: "";
    position: absolute;
    top: -7px;
    left: 50%;
    transform: translateX(-50%) rotate(45deg);
    width: 14px;
    height: 14px;
    background: linear-gradient(135deg, #2E5339, #4A7C59);
    border-radius: 3px;
}

/* ---------- chat messages (Streamlit native st.chat_message) ---------- */
[data-testid="stChatMessage"] {
    background: transparent !important;
    padding: 6px 0 !important;
    border: none !important;
    margin: 10px 0 !important;
    gap: 12px !important;
    animation: sa-slide 0.35s ease;
}

/* the avatar circle */
[data-testid="stChatMessage"] > [data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessage"] > [data-testid="stChatMessageAvatarAssistant"],
[data-testid="stChatMessage"] > div:first-child img,
[data-testid="stChatMessage"] > div:first-child {
    background: linear-gradient(135deg, #2E5339 0%, #4A7C59 100%) !important;
    border-radius: 50% !important;
    box-shadow: 0 4px 12px rgba(46, 83, 57, 0.22) !important;
    color: #FFFFFF !important;
    font-size: 1.05rem !important;
    flex-shrink: 0;
}

/* the message body container */
[data-testid="stChatMessage"] [data-testid="stChatMessageContent"],
[data-testid="stChatMessage"] > div:last-child {
    background: rgba(255, 255, 255, 0.92) !important;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(232, 230, 216, 0.9) !important;
    border-radius: 22px 22px 22px 6px !important;
    padding: 14px 18px !important;
    box-shadow: 0 6px 18px rgba(46, 83, 57, 0.10) !important;
    color: #1F2937 !important;
    font-size: 0.96rem !important;
    line-height: 1.55 !important;
    max-width: calc(100% - 60px);
}

/* user message: right-aligned with sage gradient */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    flex-direction: row-reverse !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"],
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) > div:last-child {
    background: linear-gradient(135deg, #4A7C59 0%, #6B8E5C 100%) !important;
    border: none !important;
    color: #FFFFFF !important;
    border-radius: 22px 22px 6px 22px !important;
    box-shadow: 0 6px 18px rgba(74, 124, 89, 0.28) !important;
    font-weight: 500;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] p,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) > div:last-child p {
    color: #FFFFFF !important;
}

/* paragraphs and lists inside messages */
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
    margin-bottom: 0.55rem !important;
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p:last-child {
    margin-bottom: 0 !important;
}
[data-testid="stChatMessage"] strong { color: #2E5339; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) strong { color: #FFFFFF; }

/* ---------- product cards ---------- */
.sa-product-row {
    display: flex;
    flex-wrap: wrap;
    gap: 14px;
    margin: 10px 0 6px 0;
    animation: sa-fadein 0.5s ease;
}
.sa-product-card {
    flex: 1 1 220px;
    min-width: 220px;
    max-width: 260px;
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(232, 230, 216, 0.9);
    border-radius: 20px;
    padding: 12px 12px 14px 12px;
    box-shadow: 0 10px 28px rgba(46, 83, 57, 0.10);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
.sa-product-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 18px 36px rgba(46, 83, 57, 0.16);
}
.sa-product-card img {
    width: 100%;
    height: 170px;
    object-fit: cover;
    border-radius: 14px;
    margin-bottom: 10px;
}
.sa-product-card h4 {
    font-size: 0.92rem;
    margin: 4px 2px 0 2px;
    color: #2E5339;
    font-weight: 700;
    line-height: 1.3;
}

/* ---------- questionnaire pills (Streamlit buttons) ---------- */
div[data-testid="stButton"] > button {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(10px);
    color: #2E5339;
    border: 1.5px solid rgba(74, 124, 89, 0.35);
    border-radius: 999px;
    padding: 12px 22px;
    font-weight: 600;
    font-family: 'Plus Jakarta Sans', sans-serif;
    transition: all 0.2s ease;
    width: 100%;
    box-shadow: 0 4px 12px rgba(46, 83, 57, 0.06);
}
div[data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #2E5339, #4A7C59);
    color: #FFFFFF;
    border-color: transparent;
    transform: translateY(-2px);
    box-shadow: 0 10px 22px rgba(46, 83, 57, 0.22);
}
div[data-testid="stButton"] > button:focus {
    box-shadow: 0 0 0 3px rgba(74, 124, 89, 0.25), 0 6px 18px rgba(46, 83, 57, 0.15);
    outline: none;
}

.sa-question-label {
    text-align: center;
    font-size: 1.05rem;
    font-weight: 600;
    color: #2E5339;
    margin: 18px 0 14px 0;
}

/* ---------- chat input ---------- */
[data-testid="stChatInput"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] form,
[data-testid="stChatInput"] form > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
/* The actual input pill: target the deepest div wrapping textarea + button */
[data-testid="stChatInput"] form > div > div,
[data-testid="stChatInput"] [data-baseweb="textarea"] {
    background: rgba(255, 255, 255, 0.97) !important;
    border: 1.5px solid rgba(74, 124, 89, 0.28) !important;
    border-radius: 999px !important;
    box-shadow: 0 14px 34px rgba(46, 83, 57, 0.16) !important;
    padding: 4px 6px 4px 22px !important;
    transition: all 0.2s ease !important;
    display: flex !important;
    align-items: center !important;
}
[data-testid="stChatInput"] form > div > div:focus-within,
[data-testid="stChatInput"] [data-baseweb="textarea"]:focus-within {
    border-color: rgba(74, 124, 89, 0.65) !important;
    box-shadow: 0 0 0 4px rgba(74, 124, 89, 0.14), 0 16px 38px rgba(46, 83, 57, 0.20) !important;
}
[data-testid="stChatInput"] textarea,
[data-testid="stChatInputTextArea"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    color: #1F2937 !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.97rem !important;
    padding: 14px 8px 14px 0 !important;
    min-height: 50px !important;
    resize: none !important;
}
[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stChatInputTextArea"]::placeholder {
    color: #9AA193 !important;
    font-weight: 500;
}
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #2E5339, #4A7C59) !important;
    border: none !important;
    border-radius: 50% !important;
    color: #FFFFFF !important;
    box-shadow: 0 6px 14px rgba(46, 83, 57, 0.30) !important;
    width: 42px !important;
    height: 42px !important;
    min-width: 42px !important;
    min-height: 42px !important;
    margin-right: 4px !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
[data-testid="stChatInput"] button:hover:not(:disabled) {
    transform: scale(1.06);
    box-shadow: 0 8px 18px rgba(46, 83, 57, 0.36) !important;
}
[data-testid="stChatInput"] button:disabled {
    opacity: 0.5;
}
[data-testid="stChatInput"] button svg,
[data-testid="stChatInput"] button path {
    fill: #FFFFFF !important;
    color: #FFFFFF !important;
}

/* sticky chat input area background fade */
[data-testid="stBottomBlockContainer"],
[data-testid="stBottom"] {
    background: linear-gradient(180deg, rgba(251, 250, 244, 0) 0%, rgba(251, 250, 244, 0.92) 35%, rgba(245, 243, 232, 1) 100%) !important;
    backdrop-filter: blur(8px) !important;
    padding-top: 18px !important;
    padding-bottom: 22px !important;
}

/* ---------- mobile ---------- */
@media (max-width: 640px) {
    .block-container { padding-left: 0.9rem; padding-right: 0.9rem; padding-bottom: 8rem; }
    .sa-header .logo { font-size: 1.55rem; }
    .sa-mascot-halo { width: 160px; height: 160px; }
    .sa-mascot-halo video, .sa-mascot-halo img { width: 132px; height: 132px; }
    .sa-bubble { font-size: 0.88rem; max-width: 280px; padding: 9px 16px; }
    .sa-product-card { min-width: 100%; max-width: 100%; }
    [data-testid="stChatMessage"] [data-testid="stChatMessageContent"],
    [data-testid="stChatMessage"] > div:last-child {
        font-size: 0.92rem !important;
        padding: 12px 14px !important;
    }
    [data-testid="stChatInput"] textarea { font-size: 0.92rem !important; }
}

/* ---------- animations ---------- */
@keyframes sa-fadein {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes sa-slide {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes sa-float {
    0%, 100% { transform: translateY(0); }
    50%      { transform: translateY(-8px); }
}
@keyframes sa-blink {
    50% { opacity: 0; }
}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def render_header() -> None:
    st.markdown(
        """
        <div class="sa-header">
            <div class="logo">🌿 Sigiri Ayu</div>
            <div class="tag">Nurture Your Beauty, Naturally</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@lru_cache(maxsize=4)
def _file_to_data_uri(path_str: str, mime: str) -> str:
    data = Path(path_str).read_bytes()
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


def render_mascot(bubble_text: str = "Hi! I'm your Sigiri Ayu guide 🌿") -> None:
    if MASCOT_VIDEO.exists():
        uri = _file_to_data_uri(str(MASCOT_VIDEO), "video/webm")
        media_html = f'<video autoplay loop muted playsinline src="{uri}"></video>'
    elif MASCOT_IMAGE.exists():
        uri = _file_to_data_uri(str(MASCOT_IMAGE), "image/png")
        media_html = f'<img src="{uri}" alt="mascot" />'
    else:
        media_html = '<div style="width:168px;height:168px;background:#F5F7F4;border-radius:50%;"></div>'

    st.markdown(
        f"""
        <div class="sa-hero">
            <div class="sa-mascot-halo">{media_html}</div>
            <div class="sa-bubble">{bubble_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _format_assistant_html(content: str) -> str:
    """Lightweight markdown-to-HTML for assistant messages: **bold**, line breaks, lists."""
    import re

    safe = content.replace("<", "&lt;").replace(">", "&gt;")
    safe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)
    safe = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<em>\1</em>", safe)
    safe = safe.replace("\n", "<br>")
    return safe


def render_message(role: str, content: str) -> None:
    if role == "user":
        safe = content.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
    else:
        safe = _format_assistant_html(content)
    st.markdown(
        f'<div class="sa-msg {role}"><div class="body">{safe}</div></div>',
        unsafe_allow_html=True,
    )


def assistant_bubble_html(content: str, with_caret: bool = False) -> str:
    body = _format_assistant_html(content)
    if with_caret:
        body += '<span class="sa-caret"></span>'
    return f'<div class="sa-msg assistant"><div class="body">{body}</div></div>'


def render_product_cards(product_names: List[str]) -> None:
    if not product_names:
        return
    cards_html: List[str] = ['<div class="sa-product-row">']
    for name in product_names:
        img_path = find_image(name)
        if img_path is None:
            continue
        suffix = img_path.suffix.lstrip(".").lower()
        mime = "image/jpeg" if suffix in ("jpg", "jpeg") else f"image/{suffix}"
        uri = _file_to_data_uri(str(img_path), mime)
        cards_html.append(
            f'<div class="sa-product-card"><img src="{uri}" alt="{name}" /><h4>{name}</h4></div>'
        )
    cards_html.append("</div>")
    st.markdown("\n".join(cards_html), unsafe_allow_html=True)


def render_question_label(text: str) -> None:
    st.markdown(f'<div class="sa-question-label">{text}</div>', unsafe_allow_html=True)


def bubble_text_for_stage(stage: str) -> str:
    mapping = {
        "start": "Hi! I'll help you find your perfect ritual ✨",
        "ask_category": "What are you looking for today?",
        "ask_concern": "Tell me about your main concern 🌿",
        "ask_type": "What's your skin or scalp type?",
        "recommend": "Here's what I'd recommend 💚",
        "free_chat": "Ask me anything about our products!",
        "thinking": "Let me think...",
    }
    return mapping.get(stage, "Ask me anything!")
