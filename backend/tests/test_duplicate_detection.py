from app.services.duplicate_detection import (
    check_duplicates,
    find_similar_businesses,
    name_similarity,
    normalize_business_name,
)


class TestNormalizeBusinessName:
    def test_lowercases_and_strips_punctuation(self):
        assert normalize_business_name("Joe's Taco Stand!") == "joe s taco stand"

    def test_collapses_whitespace(self):
        assert normalize_business_name("  Foo   Bar  ") == "foo bar"


class TestNameSimilarity:
    def test_exact_after_normalization(self):
        assert name_similarity("Test Kitchen", "test-kitchen") == 1.0

    def test_different_names(self):
        assert name_similarity("Sushi Palace", "Burger Barn") < 0.5

    def test_high_similarity(self):
        score = name_similarity("Golden Dragon Restaurant", "Golden Dragon Resturant")
        assert score >= 0.85


class TestFindSimilarBusinesses:
    def test_finds_match_in_same_city(self, db_session, sample_business):
        matches = find_similar_businesses(db_session, "Test Kitchen", "Berlin")
        assert len(matches) == 1
        assert matches[0].slug == "test-kitchen"
        assert matches[0].match_type == "exact"

    def test_ignores_other_cities(self, db_session, sample_business):
        matches = find_similar_businesses(db_session, "Test Kitchen", "Mumbai")
        assert matches == []

    def test_finds_fuzzy_match(self, db_session, sample_business):
        matches = find_similar_businesses(db_session, "The Test Kitchen", "Berlin")
        assert len(matches) == 1
        assert 0.75 <= matches[0].similarity < 0.90


class TestCheckDuplicates:
    def test_no_matches(self, db_session, sample_business):
        result = check_duplicates(db_session, "Brand New Place", "Berlin")
        assert not result.has_similar
        assert not result.block
        assert not result.requires_acknowledgement

    def test_blocks_exact_match(self, db_session, sample_business):
        result = check_duplicates(db_session, "Test Kitchen", "Berlin")
        assert result.block
        assert not result.requires_acknowledgement

    def test_requires_acknowledgement_for_medium_match(self, db_session, sample_business):
        result = check_duplicates(db_session, "The Test Kitchen", "Berlin")
        assert not result.block
        assert result.requires_acknowledgement
