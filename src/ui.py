"""Streamlit UI helpers: CSS injection, mascot, chat bubbles, product cards."""
from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

import streamlit as st
import streamlit.components.v1 as components

from .image_matcher import find_image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MASCOT_DIR = PROJECT_ROOT / "Mascot"
MASCOT_IMAGE = MASCOT_DIR / "mascot_image.png"
MASCOT_VIDEO = MASCOT_DIR / "Mascot Animation.webm"

# Mock retail prices in Sri Lankan Rupees
PRODUCT_PRICES: dict[str, str] = {
    "Sigiri Ayu Herbal Coconut & Hibiscus Shampoo":            "Rs. 1,290",
    "Sigiri Ayu Coconut Milk & Aloe Vera Conditioner":         "Rs. 1,190",
    "Sigiri Ayu Fenugreek & Coconut Deep Repair Hair Mask":    "Rs. 1,490",
    "Sigiri Ayu Neem & Salt Scalp Scrub":                      "Rs. 990",
    "Sigiri Ayu Hibiscus & Aloe Hair Serum":                   "Rs. 1,390",
    "Sigiri Ayu Herbal Neem & Turmeric Face Wash":             "Rs. 890",
    "Sigiri Ayu Gotukola & Turmeric Brightening Face Serum":   "Rs. 1,850",
    "Sigiri Ayu Coconut Milk & Sandalwood Moisturising Cream": "Rs. 1,390",
    "Sigiri Ayu Rice Flour & Turmeric Brightening Face Scrub": "Rs. 990",
    "Sigiri Ayu Charcoal & Neem Purifying Face Mask":          "Rs. 1,190",
    "Sigiri Ayu Aloe Vera & Sandalwood Refreshing Body Wash":  "Rs. 1,090",
    "Sigiri Ayu Coconut & Sandalwood Radiance Body Oil":       "Rs. 1,690",
    "Sigiri Ayu Coconut Milk & Sandalwood Nourishing Body Lotion": "Rs. 1,190",
    "Sigiri Ayu Sandalwood Natural Body Mist":                 "Rs. 1,290",
    "Sigiri Ayu Salt & Rice Flour Exfoliating Body Scrub":     "Rs. 890",
    "Sigiri Ayu Coconut & Aloe Vera Nourishing Lip Balm":      "Rs. 490",
    "Sigiri Ayu Sugar & Rice Flour Exfoliating Lip Scrub":     "Rs. 590",
    "Sigiri Ayu Aloe Vera & Coconut Hand Cream":               "Rs. 790",
    "Sigiri Ayu Coconut & Aloe Vera Intensive Foot Cream":     "Rs. 890",
    "Sigiri Ayu Neem & Salt Purifying Foot Scrub":             "Rs. 890",
    "Sigiri Ayu Coconut Oil Cuticle Treatment":                "Rs. 790",
    "Sigiri Ayu Plant Extract Nail Strengthening Treatment":   "Rs. 950",
    "Sigiri Ayu Aloe Vera & Neem Gentle Intimate Wash":        "Rs. 990",
    "Sigiri Ayu Aloe Vera & Coconut Soothing Shaving Cream":   "Rs. 890",
}

# Incrementing counter so each card group gets a unique DOM id (Streamlit persists DOM across rerenders)
_card_group_counter: int = 0


CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* ---------- base ---------- */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: #FFFFFF !important;
    font-family: 'Plus Jakarta Sans', -apple-system, 'Segoe UI', Roboto, sans-serif !important;
    color: #1F2937;
}
[data-testid="stHeader"] { background: transparent; }

/* Make Streamlit's internal markdown wrappers fully transparent
   so they don't create a visible white box behind the mascot */
[data-testid="stMarkdownContainer"],
[data-testid="stVerticalBlockBorderWrapper"],
.element-container {
    background: transparent !important;
}
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
    max-width: 1200px;
    width: 100%;
    padding-top: 1.2rem;
    padding-bottom: 9rem;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
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
    width: 290px;
    height: 290px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: transparent;
    animation: sa-float 5s ease-in-out infinite;
}
.sa-mascot-halo::before { display: none; }
.sa-mascot-halo video, .sa-mascot-halo img {
    position: relative;
    width: 248px;
    height: 248px;
    object-fit: contain;
    z-index: 1;
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
    background: rgba(245, 243, 232, 0.96) !important;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(210, 205, 185, 0.80) !important;
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
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 18px;
    margin: 12px 0 8px 0;
    animation: sa-fadein 0.5s ease;
}
.sa-product-card {
    background: #FAF8F2;
    border: 1px solid rgba(200, 195, 175, 0.70);
    border-radius: 20px;
    padding: 14px 14px 16px 14px;
    box-shadow: 0 6px 20px rgba(46, 83, 57, 0.08);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    display: flex;
    flex-direction: column;
    cursor: pointer;
}
.sa-product-price {
    display: inline-block;
    margin: 8px 2px 0 2px;
    font-size: 0.86rem;
    font-weight: 700;
    color: #2E5339;
    background: rgba(74, 124, 89, 0.10);
    border-radius: 999px;
    padding: 3px 12px;
    letter-spacing: 0.2px;
}
.sa-product-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 18px 36px rgba(46, 83, 57, 0.16);
}
.sa-product-card img {
    width: 100%;
    aspect-ratio: 4 / 3;
    object-fit: contain;
    background: rgba(255, 255, 255, 0.70);
    border-radius: 14px;
    margin-bottom: 10px;
    padding: 8px;
    display: block;
}
.sa-product-card h4 {
    font-size: 0.95rem;
    margin: 4px 2px 0 2px;
    color: #2E5339;
    font-weight: 700;
    line-height: 1.3;
    flex: 1;
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
    background: rgba(255, 255, 255, 0.98) !important;
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
    background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.92) 35%, rgba(255,255,255,1) 100%) !important;
    backdrop-filter: blur(8px) !important;
    padding-top: 18px !important;
    padding-bottom: 22px !important;
}

/* ---------- mobile ---------- */
@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-bottom: 7rem;
    }
    .sa-header .logo { font-size: 1.45rem; }
    .sa-mascot-halo { width: 200px; height: 200px; }
    .sa-mascot-halo video, .sa-mascot-halo img { width: 172px; height: 172px; }
    .sa-bubble { font-size: 0.86rem; max-width: 260px; padding: 8px 14px; }

    /* Horizontal scroll strip on mobile */
    .sa-product-row {
        display: flex;
        flex-wrap: nowrap;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        scroll-snap-type: x mandatory;
        gap: 12px;
        padding-bottom: 10px;
        /* hide scrollbar but keep scroll */
        scrollbar-width: none;
    }
    .sa-product-row::-webkit-scrollbar { display: none; }
    .sa-product-card {
        flex: 0 0 220px;
        scroll-snap-align: start;
    }
    .sa-product-card img { aspect-ratio: 1 / 1; }

    [data-testid="stChatMessage"] [data-testid="stChatMessageContent"],
    [data-testid="stChatMessage"] > div:last-child {
        font-size: 0.92rem !important;
        padding: 12px 14px !important;
        max-width: calc(100% - 48px);
    }
    [data-testid="stChatInput"] textarea { font-size: 0.92rem !important; }

    /* questionnaire buttons: single column on phone */
    div[data-testid="stButton"] > button {
        font-size: 0.9rem;
        padding: 10px 16px;
    }
}

/* ---------- product image modal ---------- */
.sa-modal-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 16, 0.78);
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
    z-index: 99999;
    align-items: center;
    justify-content: center;
}
.sa-modal-overlay.sa-modal-open {
    display: flex;
    animation: sa-fadein 0.18s ease;
}
.sa-modal-box {
    position: relative;
    background: #FFFFFF;
    border-radius: 24px;
    padding: 28px 28px 22px 28px;
    max-width: min(680px, 92vw);
    width: 100%;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    box-shadow: 0 32px 80px rgba(0, 0, 0, 0.40);
    overflow-y: auto;
}
.sa-modal-close {
    position: absolute;
    top: 14px;
    right: 16px;
    background: rgba(46, 83, 57, 0.10);
    border: none;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    font-size: 1.05rem;
    color: #2E5339;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s ease;
    font-family: inherit;
    line-height: 1;
}
.sa-modal-close:hover { background: rgba(46, 83, 57, 0.22); }
.sa-modal-img {
    width: 100%;
    max-height: 58vh;
    object-fit: contain;
    border-radius: 16px;
    background: #FAF8F2;
    padding: 12px;
}
.sa-modal-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: #2E5339;
    text-align: center;
    margin: 0;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
@media (max-width: 768px) {
    .sa-modal-box { padding: 20px 16px 18px 16px; border-radius: 18px; }
    .sa-modal-img { max-height: 48vh; }
    .sa-modal-name { font-size: 0.97rem; }
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


@lru_cache(maxsize=64)
def _file_to_data_uri(path_str: str, mime: str) -> str:
    """Read a file and return a base64 data URI.
    For images, resize to max 700px to reduce HTML payload and improve render speed.
    """
    path = Path(path_str)
    if mime.startswith("image/"):
        try:
            from PIL import Image
            import io
            with Image.open(path) as img:
                img.thumbnail((1400, 1400), Image.LANCZOS)
                buf = io.BytesIO()
                if img.mode in ("RGBA", "LA", "PA"):
                    img = img.convert("RGBA")
                    img.save(buf, format="PNG", optimize=True)
                    out_mime = "image/png"
                else:
                    img = img.convert("RGB")
                    img.save(buf, format="JPEG", quality=95, optimize=True)
                    out_mime = "image/jpeg"
                data = buf.getvalue()
            return f"data:{out_mime};base64,{base64.b64encode(data).decode('ascii')}"
        except Exception:
            pass  # fall through to raw read
    data = path.read_bytes()
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
    """Render product cards inside a components.v1.html iframe so JS onclick handlers work.
    The modal is injected into window.parent.document to cover the full Streamlit page."""
    global _card_group_counter
    if not product_names:
        return

    card_items: List[str] = []
    for name in product_names:
        img_path = find_image(name)
        if img_path is None:
            continue
        suffix = img_path.suffix.lstrip(".").lower()
        mime = "image/jpeg" if suffix in ("jpg", "jpeg") else f"image/{suffix}"
        uri = _file_to_data_uri(str(img_path), mime)
        price = PRODUCT_PRICES.get(name, "")
        price_html = f'<span class="sa-price">{price}</span>' if price else ""
        # Escape for JS string literals (single-quoted)
        safe_uri = uri  # data URIs contain only base64/ASCII – safe
        safe_name = name.replace("\\", "\\\\").replace("'", "\\'").replace('"', "&quot;")
        safe_price = price.replace("'", "\\'")
        card_items.append(
            f'<div class="card" onclick="openModal(\'{safe_uri}\',\'{safe_name}\',\'{safe_price}\')">' 
            f'<img src="{uri}" alt="{name}" />'
            f'<h4>{name}</h4>{price_html}</div>'
        )

    if not card_items:
        return

    num_cards = len(card_items)
    # Estimate row count assuming ~4 cards per row; 340 px per row
    rows = max(1, (num_cards + 3) // 4)
    height = rows * 340 + 24

    html_doc = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{background:transparent;font-family:'Plus Jakarta Sans',sans-serif;padding:4px 0 12px;}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:16px;}}
.card{{background:#FAF8F2;border:1px solid rgba(200,195,175,.7);border-radius:20px;padding:14px 14px 16px;
  box-shadow:0 6px 20px rgba(46,83,57,.08);display:flex;flex-direction:column;cursor:pointer;
  transition:transform .25s ease,box-shadow .25s ease;}}
.card:hover{{transform:translateY(-4px);box-shadow:0 18px 36px rgba(46,83,57,.16);}}
.card img{{width:100%;aspect-ratio:4/3;object-fit:contain;background:rgba(255,255,255,.7);
  border-radius:14px;margin-bottom:10px;padding:8px;display:block;}}
.card h4{{font-size:.95rem;margin:4px 2px 0;color:#2E5339;font-weight:700;line-height:1.3;flex:1;}}
.sa-price{{display:inline-block;margin:8px 2px 0;font-size:.86rem;font-weight:700;color:#2E5339;
  background:rgba(74,124,89,.1);border-radius:999px;padding:3px 12px;}}
</style></head><body>
<div class="grid">{''.join(card_items)}</div>
<script>
function openModal(src,name,price){{
  var pdoc=window.parent.document;
  /* inject modal CSS into parent page once */
  if(!pdoc.getElementById('_sa_modal_css')){{  
    var s=pdoc.createElement('style');s.id='_sa_modal_css';
    s.textContent=
      '.sa-pm{{display:none;position:fixed;inset:0;background:rgba(15,23,16,.78);'+
      'backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);z-index:99999;'+
      'align-items:center;justify-content:center;}}'+
      '.sa-pm.open{{display:flex;}}'+
      '.sa-pmbox{{position:relative;background:#fff;border-radius:24px;padding:28px;'+
      'max-width:min(680px,92vw);width:100%;max-height:90vh;display:flex;flex-direction:column;'+
      'align-items:center;gap:16px;box-shadow:0 32px 80px rgba(0,0,0,.4);overflow-y:auto;}}'+
      '.sa-pmclose{{position:absolute;top:14px;right:16px;background:rgba(46,83,57,.1);border:none;'+
      'border-radius:50%;width:36px;height:36px;font-size:1.1rem;color:#2E5339;cursor:pointer;'+
      'display:flex;align-items:center;justify-content:center;}}'+
      '.sa-pmclose:hover{{background:rgba(46,83,57,.22);}}'+
      '.sa-pmimg{{width:100%;max-height:58vh;object-fit:contain;border-radius:16px;background:#FAF8F2;padding:12px;}}'+
      '.sa-pmname{{font-size:1.1rem;font-weight:700;color:#2E5339;text-align:center;'+
      'font-family:\'Plus Jakarta Sans\',sans-serif;margin:0;}}'+
      '.sa-pmprice{{display:inline-block;font-size:1rem;font-weight:700;color:#2E5339;'+
      'background:rgba(74,124,89,.1);border-radius:999px;padding:6px 18px;}}';
    pdoc.head.appendChild(s);
  }}
  /* inject modal DOM into parent page once */
  if(!pdoc.getElementById('_sa_pm')){{  
    var m=pdoc.createElement('div');
    m.id='_sa_pm';m.className='sa-pm';
    m.innerHTML=
      '<div class="sa-pmbox">'+
      '<button class="sa-pmclose" id="_sa_pmclose">&#x2715;</button>'+
      '<img id="_sa_pmimg" class="sa-pmimg" src="" alt=""/>'+
      '<p id="_sa_pmname" class="sa-pmname"></p>'+
      '<span id="_sa_pmprice" class="sa-pmprice"></span>'+
      '</div>';
    pdoc.body.appendChild(m);
    pdoc.getElementById('_sa_pmclose').addEventListener('click',closeModal);
    m.addEventListener('click',function(e){{if(e.target===m)closeModal();}});
  }}
  pdoc.getElementById('_sa_pmimg').src=src;
  pdoc.getElementById('_sa_pmname').textContent=name;
  var p=pdoc.getElementById('_sa_pmprice');
  p.textContent=price;p.style.display=price?'inline-block':'none';
  pdoc.getElementById('_sa_pm').classList.add('open');
  pdoc.body.style.overflow='hidden';
}}
function closeModal(){{
  var pdoc=window.parent.document;
  pdoc.getElementById('_sa_pm').classList.remove('open');
  pdoc.body.style.overflow='';
}}
</script>
</body></html>"""

    components.html(html_doc, height=height, scrolling=False)

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
