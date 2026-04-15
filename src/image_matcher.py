"""Map product names to image file paths on disk."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = PROJECT_ROOT / "Images"


@lru_cache(maxsize=1)
def _image_index() -> Dict[str, Path]:
    index: Dict[str, Path] = {}
    if not IMAGES_DIR.exists():
        return index
    for path in IMAGES_DIR.iterdir():
        if path.is_file() and path.suffix.lower() in {".jpeg", ".jpg", ".png", ".webp"}:
            index[path.stem.strip().lower()] = path
    return index


def find_image(product_name: str) -> Optional[Path]:
    """Return the matching image file for a product name, or None if not found."""
    if not product_name:
        return None
    index = _image_index()
    key = product_name.strip().lower()
    if key in index:
        return index[key]
    # Fallback: substring match both directions.
    for stem, path in index.items():
        if key in stem or stem in key:
            return path
    return None


def all_image_names() -> list[str]:
    return sorted(p.stem for p in _image_index().values())
