from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.business import Business
from app.models.enums import ReviewStatus
from app.models.review import Review
from app.models.structured_score import StructuredScore
from app.schemas import ReviewCreate, ReviewOut, StructuredScoreOut

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewOut)
def create_review(
    data: ReviewCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if not data.consent_given:
        raise HTTPException(
            status_code=400, detail="Consent is required before submitting a review"
        )

    business = db.query(Business).filter(Business.id == data.business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")

    review = Review(
        business_id=data.business_id,
        user_id=user.id,
        visit_type=data.visit_type,
        visit_date=data.visit_date,
        notes=data.notes,
        consent_given=data.consent_given,
        status=ReviewStatus.APPROVED,
    )
    db.add(review)
    db.flush()

    score = StructuredScore(
        review_id=review.id,
        cleanliness=data.structured_score.cleanliness,
        staff_hygiene=data.structured_score.staff_hygiene,
        food_handling=data.structured_score.food_handling,
        packaging=data.structured_score.packaging,
        water_confidence=data.structured_score.water_confidence,
        oil_freshness_concern=data.structured_score.oil_freshness_concern,
        taste_optional=data.structured_score.taste_optional,
    )
    db.add(score)
    db.commit()
    db.refresh(review)

    out = ReviewOut.model_validate(review)
    out.structured_score = StructuredScoreOut.model_validate(score)
    out.user_name = user.full_name or user.email.split("@")[0]
    return out


@router.get("/me", response_model=list[ReviewOut])
def my_reviews(db: Session = Depends(get_db), user=Depends(get_current_user)):
    reviews = (
        db.query(Review)
        .options(joinedload(Review.structured_score), joinedload(Review.user))
        .filter(Review.user_id == user.id)
        .order_by(Review.created_at.desc())
        .all()
    )
    result = []
    for r in reviews:
        out = ReviewOut.model_validate(r)
        out.user_name = user.full_name or user.email.split("@")[0]
        result.append(out)
    return result
