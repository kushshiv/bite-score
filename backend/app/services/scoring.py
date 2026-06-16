from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.business import Business
from app.models.enums import BadgeType, FlagTargetType, ReviewStatus
from app.models.evidence_upload import EvidenceUpload
from app.models.report_flag import ReportFlag
from app.models.review import Review
from app.models.structured_score import StructuredScore
from app.models.verification_badge import VerificationBadge

SCORE_WEIGHTS = {
    "cleanliness": 0.30,
    "food_handling": 0.20,
    "staff_hygiene": 0.15,
    "packaging": 0.10,
    "water_confidence": 0.10,
    "evidence_credibility": 0.10,
    "consistency": 0.05,
}

METHODOLOGY = (
    "BiteScore combines structured community observations with transparent weighting: "
    "30% hygiene/cleanliness, 20% food handling, 15% staff hygiene, 10% packaging, "
    "10% water safety confidence, 10% evidence credibility, and 5% consistency weighting. "
    "Scores are platform-derived community signals, not government certifications."
)


def _score_to_percent(value: float) -> float:
    return round((value / 5.0) * 100, 1)


def compute_review_score(score: StructuredScore, has_evidence: bool) -> float:
    evidence_score = 5.0 if has_evidence else 3.0
    weighted = (
        score.cleanliness * SCORE_WEIGHTS["cleanliness"]
        + score.food_handling * SCORE_WEIGHTS["food_handling"]
        + score.staff_hygiene * SCORE_WEIGHTS["staff_hygiene"]
        + score.packaging * SCORE_WEIGHTS["packaging"]
        + score.water_confidence * SCORE_WEIGHTS["water_confidence"]
        + evidence_score * SCORE_WEIGHTS["evidence_credibility"]
        + score.cleanliness * SCORE_WEIGHTS["consistency"]
    )
    if score.oil_freshness_concern:
        weighted -= 0.3
    return round(max(0, min(5, weighted)), 2)


def compute_business_score(db: Session, business_id: int) -> dict:
    reviews = (
        db.query(Review)
        .filter(Review.business_id == business_id, Review.status == ReviewStatus.APPROVED)
        .all()
    )
    if not reviews:
        return {
            "overall": 0,
            "overall_percent": 0,
            "review_count": 0,
            "breakdown": {},
            "methodology": METHODOLOGY,
            "trust_indicators": ["low_sample_size"],
        }

    totals = {
        "cleanliness": 0.0,
        "food_handling": 0.0,
        "staff_hygiene": 0.0,
        "packaging": 0.0,
        "water_confidence": 0.0,
        "evidence_credibility": 0.0,
    }
    review_scores: list[float] = []

    for review in reviews:
        if not review.structured_score:
            continue
        has_evidence = bool(review.evidence_uploads)
        rs = compute_review_score(review.structured_score, has_evidence)
        review_scores.append(rs)
        s = review.structured_score
        totals["cleanliness"] += s.cleanliness
        totals["food_handling"] += s.food_handling
        totals["staff_hygiene"] += s.staff_hygiene
        totals["packaging"] += s.packaging
        totals["water_confidence"] += s.water_confidence
        totals["evidence_credibility"] += 5.0 if has_evidence else 3.0

    count = len(review_scores) or 1
    breakdown = {k: round(v / count, 2) for k, v in totals.items()}
    overall = round(sum(review_scores) / len(review_scores), 2) if review_scores else 0

    business = db.query(Business).filter(Business.id == business_id).first()
    trust_indicators = compute_trust_indicators(db, business, reviews, review_scores)

    return {
        "overall": overall,
        "overall_percent": _score_to_percent(overall),
        "review_count": len(reviews),
        "breakdown": breakdown,
        "methodology": METHODOLOGY,
        "trust_indicators": trust_indicators,
    }


def _as_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def compute_trust_indicators(
    db: Session,
    business: Business | None,
    reviews: list[Review],
    review_scores: list[float],
) -> list[str]:
    indicators: list[str] = []

    if len(reviews) < 5:
        indicators.append("low_sample_size")

    verified_evidence = (
        db.query(EvidenceUpload)
        .filter(
            EvidenceUpload.business_id == business.id if business else None,
            EvidenceUpload.verified == True,  # noqa: E712
        )
        .count()
        if business
        else 0
    )
    if verified_evidence > 0:
        indicators.append("verified_evidence")

    if business:
        flag_count = (
            db.query(ReportFlag)
            .filter(
                ReportFlag.target_type == FlagTargetType.BUSINESS,
                ReportFlag.target_id == business.id,
            )
            .count()
        )
        if flag_count >= 2:
            indicators.append("repeated_complaints")

        if business.claimed_by_id:
            indicators.append("owner_claimed")

        badges = (
            db.query(VerificationBadge).filter(VerificationBadge.business_id == business.id).all()
        )
        badge_types = {b.badge_type for b in badges}
        if BadgeType.VERIFIED in badge_types:
            indicators.append("moderation_reviewed")
        if BadgeType.HIGH_CONFIDENCE in badge_types:
            indicators.append("high_confidence")
        if BadgeType.UNDER_REVIEW in badge_types:
            indicators.append("under_review")

    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    recent = [r for r in reviews if r.created_at and _as_utc(r.created_at) >= cutoff]
    older = [r for r in reviews if r.created_at and _as_utc(r.created_at) < cutoff]
    if recent and older and len(review_scores) >= 5:
        recent_avg = sum(review_scores[-len(recent) :]) / len(recent)
        older_avg = sum(review_scores[: len(older)]) / len(older)
        if recent_avg > older_avg + 0.3:
            indicators.append("recent_improvement_trend")

    return indicators
