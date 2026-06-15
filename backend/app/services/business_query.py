from sqlalchemy import or_
from sqlalchemy.orm import Query, Session, joinedload

from app.models.business import Business
from app.models.category import Category
from app.models.enums import BadgeType
from app.models.location import Location
from app.models.verification_badge import VerificationBadge
from app.schemas import BadgeOut, BusinessListItem, CategoryOut, LocationOut
from app.services.geo import haversine_km
from app.services.scoring import compute_business_score


def build_business_query(
    db: Session,
    *,
    q: str | None = None,
    city: str | None = None,
    category: str | None = None,
    verified_only: bool = False,
) -> Query:
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
    return query


def business_to_list_item(db: Session, business: Business) -> BusinessListItem:
    score_data = compute_business_score(db, business.id)
    return BusinessListItem(
        id=business.id,
        name=business.name,
        slug=business.slug,
        business_type=business.business_type,
        category=CategoryOut.model_validate(business.category) if business.category else None,
        location=LocationOut.model_validate(business.location) if business.location else None,
        cover_image_url=business.cover_image_url,
        overall_score=score_data["overall"],
        overall_percent=score_data["overall_percent"],
        review_count=score_data["review_count"],
        badges=[BadgeOut.model_validate(b) for b in business.badges],
    )


def businesses_in_area(
    db: Session,
    *,
    q: str | None = None,
    city: str | None = None,
    category: str | None = None,
    verified_only: bool = False,
    near_lat: float | None = None,
    near_lng: float | None = None,
    radius_km: float = 25.0,
) -> list[BusinessListItem]:
    query = build_business_query(
        db,
        q=q,
        city=city,
        category=category,
        verified_only=verified_only,
    )
    businesses = query.limit(100).all()
    items = [business_to_list_item(db, b) for b in businesses]

    if near_lat is None or near_lng is None:
        return items

    nearby: list[BusinessListItem] = []
    for item in items:
        loc = item.location
        if loc and loc.latitude is not None and loc.longitude is not None:
            dist = haversine_km(near_lat, near_lng, loc.latitude, loc.longitude)
            if dist <= radius_km:
                nearby.append(item.model_copy(update={"distance_km": round(dist, 1)}))
    return nearby
