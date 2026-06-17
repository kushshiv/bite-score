from app.services.business_create import slugify, unique_slug


class TestSlugify:
    def test_basic(self):
        assert slugify("Joe's Taco Stand") == "joe-s-taco-stand"

    def test_empty_fallback(self):
        assert slugify("!!!") == "place"


class TestUniqueSlug:
    def test_appends_suffix(self, db_session, sample_business):
        assert unique_slug(db_session, "test-kitchen") == "test-kitchen-2"

    def test_returns_base_when_free(self, db_session):
        assert unique_slug(db_session, "brand-new-place") == "brand-new-place"
