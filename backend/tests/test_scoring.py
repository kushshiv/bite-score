from datetime import date

from app.models.enums import ReviewStatus, VisitType
from app.models.review import Review
from app.models.structured_score import StructuredScore
from app.services.scoring import METHODOLOGY, compute_business_score, compute_review_score


def _make_score(**kwargs) -> StructuredScore:
    defaults = {
        "review_id": 1,
        "cleanliness": 4.0,
        "staff_hygiene": 4.0,
        "food_handling": 4.0,
        "packaging": 4.0,
        "water_confidence": 4.0,
        "oil_freshness_concern": False,
    }
    defaults.update(kwargs)
    return StructuredScore(**defaults)


def test_compute_review_score_with_evidence():
    score = _make_score(
        cleanliness=5.0, food_handling=5.0, staff_hygiene=5.0, packaging=5.0, water_confidence=5.0
    )
    result = compute_review_score(score, has_evidence=True)
    assert result == 5.0


def test_compute_review_score_oil_concern_reduces_score():
    score = _make_score(oil_freshness_concern=True)
    with_concern = compute_review_score(score, has_evidence=False)
    without_concern = compute_review_score(_make_score(), has_evidence=False)
    assert with_concern < without_concern


def test_compute_business_score_empty_reviews(db_session, sample_business):
    result = compute_business_score(db_session, sample_business.id)
    assert result["overall"] == 0
    assert result["review_count"] == 0
    assert "low_sample_size" in result["trust_indicators"]
    assert result["methodology"] == METHODOLOGY


def test_compute_business_score_with_reviews(db_session, sample_business, sample_review):
    result = compute_business_score(db_session, sample_business.id)
    assert result["review_count"] == 1
    assert result["overall"] > 0
    assert result["overall_percent"] > 0
    assert "cleanliness" in result["breakdown"]


def test_compute_business_score_multiple_reviews(db_session, sample_business, test_user):
    for i in range(5):
        review = Review(
            business_id=sample_business.id,
            user_id=test_user.id,
            visit_type=VisitType.DINE_IN,
            visit_date=date(2026, 1, i + 1),
            consent_given=True,
            status=ReviewStatus.APPROVED,
        )
        db_session.add(review)
        db_session.flush()
        db_session.add(
            StructuredScore(
                review_id=review.id,
                cleanliness=4.0,
                staff_hygiene=4.0,
                food_handling=4.0,
                packaging=4.0,
                water_confidence=4.0,
            )
        )
    db_session.commit()

    result = compute_business_score(db_session, sample_business.id)
    assert result["review_count"] == 5
    assert "low_sample_size" not in result["trust_indicators"]
