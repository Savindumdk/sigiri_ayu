"""Load brand and product data from the project files into retrievable chunks."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BRAND_FILE = PROJECT_ROOT / "Sigiri_Ayu_Details"
PRODUCTS_FILE = PROJECT_ROOT / "Sigiri_Ayu_Product_Descriptions.md"


@dataclass
class Chunk:
    id: str
    type: str  # "product" or "brand"
    name: str
    text: str
    category: Optional[str] = None
    metadata: dict = field(default_factory=dict)


_PRODUCT_NAME_RE = re.compile(r"\*\*Product Name:\s*(.+?)\*\*")
_SECTION_RE = re.compile(r"\*\*([A-Za-z /]+?):\*\*\s*\n?(.*?)(?=\n\*\*[A-Za-z /]+?:\*\*|\Z)", re.DOTALL)


def _clean(text: str) -> str:
    return text.strip().replace("\r\n", "\n")


def _split_products(raw: str) -> List[str]:
    """Split the markdown file on `---` horizontal rules, keeping only blocks with a Product Name."""
    parts = [p.strip() for p in raw.split("\n---\n")]
    return [p for p in parts if "**Product Name:" in p]


def _parse_product_block(block: str) -> Optional[dict]:
    name_match = _PRODUCT_NAME_RE.search(block)
    if not name_match:
        return None
    name = name_match.group(1).strip()

    fields = {}
    for match in _SECTION_RE.finditer(block):
        key = match.group(1).strip()
        value = match.group(2).strip()
        fields[key] = value

    category = fields.get("Category", "")
    description = fields.get("Description", "")
    ingredients = fields.get("Key Ingredients", "")
    base_composition = fields.get("Base Composition", "")
    benefits = fields.get("Benefits", "")
    suitability = (
        fields.get("Skin / Scalp Type Suitability")
        or fields.get("Skin Type Suitability")
        or fields.get("Scalp Type Suitability")
        or ""
    )
    usage = fields.get("Usage Instructions", "")
    safety = fields.get("Safety Information", "")

    text_parts = [
        f"Product: {name}",
        f"Category: {category}" if category else "",
        f"Description: {description}" if description else "",
        f"Key Ingredients:\n{ingredients}" if ingredients else "",
        f"Benefits:\n{benefits}" if benefits else "",
        f"Suitability: {suitability}" if suitability else "",
        f"Usage: {usage}" if usage else "",
        f"Safety: {safety}" if safety else "",
    ]
    text = "\n\n".join(p for p in text_parts if p)

    return {
        "name": name,
        "category": category,
        "description": description,
        "ingredients": ingredients,
        "base_composition": base_composition,
        "benefits": benefits,
        "suitability": suitability,
        "usage": usage,
        "safety": safety,
        "text": text,
    }


def load_products(path: Path = PRODUCTS_FILE) -> List[Chunk]:
    raw = _clean(path.read_text(encoding="utf-8"))
    blocks = _split_products(raw)
    chunks: List[Chunk] = []
    for idx, block in enumerate(blocks):
        parsed = _parse_product_block(block)
        if not parsed:
            continue
        chunks.append(
            Chunk(
                id=f"product_{idx}",
                type="product",
                name=parsed["name"],
                text=parsed["text"],
                category=parsed["category"],
                metadata={k: v for k, v in parsed.items() if k not in ("name", "text")},
            )
        )
    return chunks


def load_brand(path: Path = BRAND_FILE) -> List[Chunk]:
    """Split brand file into semantic chunks using section markers."""
    raw = _clean(path.read_text(encoding="utf-8"))

    # The brand file uses emoji-prefixed headings like "🌸 Brand Philosophy".
    # Split on lines that look like headings (start with an emoji + text, no period).
    lines = raw.split("\n")
    sections: List[tuple[str, list[str]]] = []
    current_title = "Overview"
    current_body: List[str] = []

    heading_re = re.compile(r"^[^\w\s]{1,3}\s*[A-Z][A-Za-z ’'&–-]+$")

    for line in lines:
        stripped = line.strip()
        if not stripped:
            current_body.append("")
            continue
        if heading_re.match(stripped) and len(stripped) < 60:
            if current_body:
                sections.append((current_title, current_body))
            current_title = stripped
            current_body = []
        else:
            current_body.append(line)
    if current_body:
        sections.append((current_title, current_body))

    chunks: List[Chunk] = []
    for idx, (title, body) in enumerate(sections):
        body_text = "\n".join(body).strip()
        if not body_text:
            continue
        text = f"Brand Section: {title}\n\n{body_text}"
        chunks.append(
            Chunk(
                id=f"brand_{idx}",
                type="brand",
                name=title,
                text=text,
                category="Brand",
                metadata={"section": title},
            )
        )
    return chunks


def load_all_chunks() -> List[Chunk]:
    """Return the full corpus: brand chunks + product chunks."""
    return load_brand() + load_products()


def get_product_names() -> List[str]:
    return [c.name for c in load_products()]
