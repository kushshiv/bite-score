from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.db.session import get_db
from app.models.business import Business
from app.models.category import Category
from app.models.enums import BadgeType, ReviewStatus
from app.models.evidence_upload import EvidenceUpload
from app.models.location import Location
from app.models.review import Review
from app.models.verification_badge import VerificationBadge
from app.schemas import (
    BadgeOut,
    BusinessDetail,
    BusinessListItem,
    CategoryOut,
    EvidenceOut,
    LocationOut,
    ReviewOut,
    ScoreBreakdown,
)
from app.services.geo import haversine_km
from app.services.scoring import compute_business_score

router = APIRouter(prefix="/businesses", tags=["businesses"])


def _business_to_list_item(db: Session, business: Business) -> BusinessListItem:
    score_data = compute_business_score(db, business.id)
    return BusinessListItem(
        id=business.id,
        name=business.name,
        slug=business.slug,
        business_type=business.business_type,
        category=CategoryOut.model_validate(business.category) if business.category else None,
        location=LocationOut.model_validate(business.location) if business.location else None,
        overall_score=score_data["overall"],
        overall_percent=score_data["overall_percent"],
        review_count=score_data["review_count"],
        badges=[BadgeOut.model_validate(b) for b in business.badges],
    )


@router.get("", response_model=list[BusinessListItem])
def list_businesses(
    db: Session = Depends(get_db),
    q: str | None = None,
    city: str | None = None,
    category: str | None = None,
    min_score: float | None = None,
    verified_only: bool = False,
    high_trust: bool = False,
    near_lat: float | None = None,
    near_lng: float | None = None,
    radius_km: float = Query(default=25.0, le=100),
    sort: str = Query(default="score", pattern="^(score|nearby)$"),
    limit: int = Query(default=20, le=100),
    offset: int = 0,
):
    query = db.query(Business).options(
        joinedload(Business.category),
        joinedload(Business.location),
        joinedload(Business.badges),
    )

    if q:
        query = query.filter(
            or_(
                Business.name.ilike(f"%{q}%"),
                Business.description.ilike(f"%{q}%"),
            )
        )
    if city:
        query = query.join(Location).filter(Location.city == city)
    if category:
        query = query.join(Business.category).filter(Category.slug == category)
    if verified_only:
        query = query.join(Business.badges).filter(VerificationBadge.badge_type == BadgeType.VERIFIED)

    use_geo = near_lat is not None and near_lng is not None
    if use_geo:
        businesses = query.limit(100).all()
    else:
        businesses = query.offset(offset).limit(limit).all()
    items = [_business_to_list_item(db, b) for b in businesses]

    if min_score is not None:
        items = [i for i in items if i.overall_score >= min_score]
    if high_trust:
        items = [i for i in items if i.overall_score >= 4.0]

    if use_geo:
        nearby: list[BusinessListItem] = []
        for item in items:
            loc = item.location
            if loc and loc.latitude is not None and loc.longitude is not None:
                dist = haversine_km(near_lat, near_lng, loc.latitude, loc.longitude)
                if dist <= radius_km:
                    nearby.append(item.model_copy(update={"distance_km": round(dist, 1)}))
        items = nearby
        if sort == "nearby":
            items.sort(key=lambda i: i.distance_km or 9999)
        else:
            items.sort(key=lambda i: i.overall_percent, reverse=True)
        return items[:limit]
    if sort == "score":
        items.sort(key=lambda i: i.overall_percent, reverse=True)

    return items


@router.get("/{slug}", response_model=BusinessDetail)
def get_business(slug: str, db: Session = Depends(get_db)):
    business = (
        db.query(Business)
        .options(
            joinedload(Business.category),
            joinedload(Business.location),
            joinedload(Business.badges),
        )
        .filter(Business.slug == slug)
        .first()
    )
    if not business:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Business not found")

    score_data = compute_business_score(db, business.id)
    base = _business_to_list_item(db, business)
    return BusinessDetail(
        **base.model_dump(),
        description=business.description,
        status=business.status,
        claimed=bool(business.claimed_by_id),
        score=ScoreBreakdown(**score_data),
    )


@router.get("/{slug}/reviews", response_model=list[ReviewOut])
def get_business_reviews(slug: str, db: Session = Depends(get_db)):
    business = db.query(Business).filter(Business.slug == slug).first()
    if not business:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Business not found")

    reviews = (
        db.query(Review)
        .options(joinedload(Review.structured_score), joinedload(Review.user))
        .filter(Review.business_id == business.id, Review.status == ReviewStatus.APPROVED)
        .order_by(Review.created_at.desc())
        .limit(50)
        .all()
    )
    result = []
    for r in reviews:
        out = ReviewOut.model_validate(r)
        out.user_name = r.user.full_name or r.user.email.split("@")[0]
        result.append(out)
    return result


@router.get("/{slug}/evidence", response_model=list[EvidenceOut])
def get_business_evidence(slug: str, db: Session = Depends(get_db)):
    business = db.query(Business).filter(Business.slug == slug).first()
    if not business:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Business not found")

    uploads = (
        db.query(EvidenceUpload)
        .filter(EvidenceUpload.business_id == business.id)
        .order_by(EvidenceUpload.created_at.desc())
        .all()
    )
    return [
        EvidenceOut(
            id=u.id,
            file_url=f"{settings.api_base_url}/uploads/{u.file_path.split('/')[-1]}",
            mime_type=u.mime_type,
            verified=u.verified,
            created_at=u.created_at,
        )
        for u in uploads
    ]
