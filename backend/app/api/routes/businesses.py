from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.db.session import get_db
from app.models.business import Business
from app.models.enums import BadgeType, ReviewStatus
from app.models.evidence_upload import EvidenceUpload
from app.models.review import Review
from app.schemas import (
    BusinessDetail,
    BusinessFacets,
    BusinessListItem,
    CategoryFacet,
    EvidenceOut,
    ReviewOut,
    ScoreBreakdown,
)
from app.services.business_query import (
    build_business_query,
    business_to_list_item,
    businesses_in_area,
)
from app.services.scoring import compute_business_score

router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.get("/facets", response_model=BusinessFacets)
def business_facets(
    db: Session = Depends(get_db),
    q: str | None = None,
    city: str | None = None,
    near_lat: float | None = None,
    near_lng: float | None = None,
    radius_km: float = Query(default=25.0, le=100),
):
    items = businesses_in_area(
        db,
        q=q,
        city=city,
        near_lat=near_lat,
        near_lng=near_lng,
        radius_km=radius_km,
    )

    category_counts: dict[str, CategoryFacet] = {}
    high_trust = 0
    verified = 0
    safe_to_eat = 0

    for item in items:
        if item.overall_score >= 4.0:
            high_trust += 1
        if item.overall_percent >= 80:
            safe_to_eat += 1
        if any(b.badge_type == BadgeType.VERIFIED for b in item.badges):
            verified += 1
        if item.category:
            slug = item.category.slug
            if slug not in category_counts:
                category_counts[slug] = CategoryFacet(slug=slug, name=item.category.name, count=0)
            category_counts[slug].count += 1

    categories = sorted(category_counts.values(), key=lambda c: (-c.count, c.name))
    return BusinessFacets(
        total=len(items),
        high_trust=high_trust,
        verified=verified,
        safe_to_eat=safe_to_eat,
        categories=categories,
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
    use_geo = near_lat is not None and near_lng is not None

    if use_geo:
        items = businesses_in_area(
            db,
            q=q,
            city=city,
            category=category,
            verified_only=verified_only,
            near_lat=near_lat,
            near_lng=near_lng,
            radius_km=radius_km,
        )
    else:
        query = build_business_query(db, q=q, city=city, category=category, verified_only=verified_only)
        businesses = query.offset(offset).limit(limit).all()
        items = [business_to_list_item(db, b) for b in businesses]

    if min_score is not None:
        items = [i for i in items if i.overall_score >= min_score]
    if high_trust:
        items = [i for i in items if i.overall_score >= 4.0]

    if use_geo:
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
        raise HTTPException(status_code=404, detail="Business not found")

    score_data = compute_business_score(db, business.id)
    base = business_to_list_item(db, business)
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
