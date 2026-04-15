"""Tests that every parsed product has a matching image on disk."""
from src.data_loader import load_products
from src.image_matcher import find_image, all_image_names


def test_image_index_nonempty():
    assert len(all_image_names()) >= 24


def test_every_product_resolves_to_an_image():
    products = load_products()
    missing = []
    for p in products:
        img = find_image(p.name)
        if img is None or not img.exists():
            missing.append(p.name)
    assert not missing, f"No image found for: {missing}"


def test_find_image_case_insensitive():
    products = load_products()
    first = products[0]
    assert find_image(first.name.lower()) is not None
    assert find_image(first.name.upper()) is not None
