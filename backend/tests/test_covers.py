from app.services.covers import CATEGORY_COVER_IMAGES, DEFAULT_COVER_IMAGE, cover_for_category


def test_cover_for_known_category():
    assert cover_for_category("indian") == CATEGORY_COVER_IMAGES["indian"]
    assert cover_for_category("street-food") == CATEGORY_COVER_IMAGES["street-food"]


def test_cover_for_unknown_category_uses_default():
    assert cover_for_category("unknown") == DEFAULT_COVER_IMAGE
    assert cover_for_category(None) == DEFAULT_COVER_IMAGE


def test_all_seed_categories_have_covers():
    expected = {
        "indian",
        "italian",
        "street-food",
        "healthy",
        "cafe",
        "bakery",
        "asian-fusion",
        "mexican",
        "mediterranean",
        "fast-casual",
    }
    assert expected == set(CATEGORY_COVER_IMAGES.keys())
    assert all(url.startswith("https://") for url in CATEGORY_COVER_IMAGES.values())
