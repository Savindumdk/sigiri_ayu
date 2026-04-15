"""Tests for brand + product parsing."""
from src.data_loader import load_brand, load_products, load_all_chunks


def test_products_parsed_count():
    products = load_products()
    assert len(products) == 24, f"Expected 24 products, got {len(products)}"


def test_every_product_has_required_fields():
    products = load_products()
    for p in products:
        assert p.name.startswith("Sigiri Ayu"), f"Bad name: {p.name}"
        assert p.category, f"Missing category for {p.name}"
        assert p.metadata.get("description"), f"Missing description for {p.name}"
        assert p.metadata.get("ingredients"), f"Missing ingredients for {p.name}"
        assert p.metadata.get("benefits"), f"Missing benefits for {p.name}"
        assert len(p.text) > 200


def test_brand_chunks_extracted():
    brand = load_brand()
    assert len(brand) >= 3, f"Expected at least 3 brand chunks, got {len(brand)}"
    all_text = " ".join(c.text for c in brand).lower()
    assert "sigiri ayu" in all_text
    assert "ayurvedic" in all_text or "ayurveda" in all_text


def test_load_all_combines_brand_and_products():
    chunks = load_all_chunks()
    types = {c.type for c in chunks}
    assert types == {"brand", "product"}
    assert sum(1 for c in chunks if c.type == "product") == 24


def test_product_names_are_unique():
    products = load_products()
    names = [p.name for p in products]
    assert len(set(names)) == len(names), "Duplicate product names found"
