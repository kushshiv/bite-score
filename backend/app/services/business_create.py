import re

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.business import Business
from app.models.category import Category
from app.models.enums import BusinessStatus
from app.models.location import Location
from app.schemas import BusinessCreate, BusinessDetail, ScoreBreakdown
from app.services.business_query import business_to_list_item
from app.services.covers import cover_for_category
from app.services.scoring import compute_business_score


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "place"


def unique_slug(db: Session, base: str) -> str:
    slug = base
    n = 2
    while db.query(Business).filter(Business.slug == slug).first():
        slug = f"{base}-{n}"
        n += 1
    return slug


def create_business(db: Session, data: BusinessCreate) -> Business:
    category = db.query(Category).filter(Category.slug == data.category).first()
    if not category:
        raise HTTPException(status_code=400, detail=f"Unknown category: {data.category}")

    slug = unique_slug(db, slugify(data.name))
    business = Business(
        name=data.name.strip(),
        slug=slug,
        category_id=category.id,
        business_type=data.business_type,
        description=data.description,
        cover_image_url=cover_for_category(category.slug),
        status=BusinessStatus.ACTIVE,
    )
    db.add(business)
    db.flush()

    db.add(
        Location(
            business_id=business.id,
            address=data.address,
            city=data.city.strip(),
            country=data.country.strip(),
            latitude=data.latitude,
            longitude=data.longitude,
        )
    )
    db.commit()
    db.refresh(business)
    return business


def business_to_detail(db: Session, business: Business) -> BusinessDetail:
    score_data = compute_business_score(db, business.id)
    base = business_to_list_item(db, business)
    return BusinessDetail(
        **base.model_dump(),
        description=business.description,
        status=business.status,
        claimed=bool(business.claimed_by_id),
        score=ScoreBreakdown(**score_data),
    )
