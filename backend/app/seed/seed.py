import random
import re
import uuid
from datetime import date, timedelta
from pathlib import Path

from PIL import Image
from sqlalchemy.orm import joinedload

from app.config import settings

from app.core.security import get_password_hash
from app.db.migrate import run_migrations
from app.db.session import SessionLocal
from app.models import (
    Business,
    Category,
    ClaimRequest,
    EvidenceUpload,
    Location,
    Review,
    StructuredScore,
    User,
    VerificationBadge,
)
from app.models.enums import (
    BadgeType,
    BusinessType,
    ClaimStatus,
    ReviewStatus,
    UserRole,
    VisitType,
)
from app.services.covers import cover_for_category

DEMO_PASSWORD = "Demo1234!"

CITIES = [
    {"city": "Berlin", "country": "Germany", "lat": 52.52, "lng": 13.405},
    {"city": "Mumbai", "country": "India", "lat": 19.076, "lng": 72.8777},
    {"city": "Austin", "country": "USA", "lat": 30.2672, "lng": -97.7431},
]

CATEGORIES = [
    ("Indian", "indian"),
    ("Italian", "italian"),
    ("Street Food", "street-food"),
    ("Healthy", "healthy"),
    ("Cafe", "cafe"),
    ("Bakery", "bakery"),
    ("Asian Fusion", "asian-fusion"),
    ("Mexican", "mexican"),
    ("Mediterranean", "mediterranean"),
    ("Fast Casual", "fast-casual"),
]

BUSINESS_NAMES = [
    "Green Leaf Kitchen",
    "Spice Route",
    "Harbor Street Tacos",
    "Pure Bowl Co",
    "Morning Grain Bakery",
    "Riverstone Bistro",
    "Urban Dosa Cart",
    "Clean Eats Lab",
    "Saffron Table",
    "Oak & Olive",
    "Fresh Press Juicery",
    "Metro Noodle House",
    "Sunrise Poke",
    "Heritage Thali",
    "Cloud Kitchen 42",
    "Market Lane Grill",
    "Zen Ramen",
    "Farm to Fork",
    "Citrus & Sage",
    "The Honest Pantry",
    "Street Spice Berlin",
    "Mumbai Masala Hub",
    "Austin Smokehouse",
    "Trust Bowl",
    "Hygiene First Cafe",
    "Golden Wok",
    "Neighborhood Deli",
    "Craft Pizza Co",
    "Wellness Wraps",
    "Community Kitchen",
]

NOTES = [
    "Clean prep area observed during visit.",
    "Staff wore gloves and maintained hygiene standards.",
    "Packaging was secure and food was well sealed.",
    "Reported concern about oil reuse — community observation noted.",
    "Water served in sealed bottles, good confidence.",
    "Consistent experience across multiple visits.",
    "Community observation: dining area was tidy.",
    "Takeaway packaging maintained temperature and cleanliness.",
]


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug


def create_evidence_upload(
    db,
    review: Review,
    *,
    verified: bool = False,
) -> EvidenceUpload:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.jpg"
    path = upload_dir / filename
    color = (random.randint(90, 210), random.randint(90, 210), random.randint(90, 210))
    Image.new("RGB", (640, 480), color=color).save(path, "JPEG")

    upload = EvidenceUpload(
        review_id=review.id,
        business_id=review.business_id,
        file_path=str(path),
        mime_type="image/jpeg",
        verified=verified,
    )
    db.add(upload)
    return upload


def backfill_evidence_uploads(db, target: int = 15) -> None:
    existing = db.query(EvidenceUpload).count()
    if existing >= target:
        return

    reviews = (
        db.query(Review)
        .outerjoin(EvidenceUpload, EvidenceUpload.review_id == Review.id)
        .filter(EvidenceUpload.id.is_(None))
        .order_by(Review.id)
        .limit(target - existing + 10)
        .all()
    )
    created = 0
    for review in reviews:
        if existing + created >= target:
            break
        create_evidence_upload(db, review, verified=random.random() < 0.25)
        created += 1

    if created:
        db.commit()
        print(f"Backfilled {created} evidence uploads.")


def backfill_coordinates(db):
    city_coords = {c["city"]: c for c in CITIES}
    updated = 0
    for loc in db.query(Location).filter(Location.latitude.is_(None)).all():
        coords = city_coords.get(loc.city)
        if coords:
            loc.latitude = round(coords["lat"] + random.uniform(-0.04, 0.04), 6)
            loc.longitude = round(coords["lng"] + random.uniform(-0.04, 0.04), 6)
            updated += 1
    if updated:
        db.commit()
        print(f"Backfilled coordinates for {updated} locations.")


def backfill_cover_images(db):
    updated = 0
    for business in (
        db.query(Business)
        .options(joinedload(Business.category))
        .filter(Business.cover_image_url.is_(None))
        .all()
    ):
        slug = business.category.slug if business.category else None
        business.cover_image_url = cover_for_category(slug)
        updated += 1
    if updated:
        db.commit()
        print(f"Backfilled cover images for {updated} businesses.")


def seed():
    run_migrations()
    db = SessionLocal()

    if db.query(User).filter(User.email == "admin@bitescore.demo").first():
        backfill_coordinates(db)
        backfill_cover_images(db)
        backfill_evidence_uploads(db)
        print("Seed data already exists. Skipping.")
        db.close()
        return

    users = [
        User(
            email="admin@bitescore.demo",
            hashed_password=get_password_hash(DEMO_PASSWORD),
            full_name="Admin User",
            role=UserRole.ADMIN,
        ),
        User(
            email="owner@bitescore.demo",
            hashed_password=get_password_hash(DEMO_PASSWORD),
            full_name="Business Owner",
            role=UserRole.BUSINESS_OWNER,
        ),
        User(
            email="user@bitescore.demo",
            hashed_password=get_password_hash(DEMO_PASSWORD),
            full_name="Demo User",
            role=UserRole.USER,
        ),
        User(
            email="moderator@bitescore.demo",
            hashed_password=get_password_hash(DEMO_PASSWORD),
            full_name="Moderator",
            role=UserRole.MODERATOR,
        ),
    ]
    for i in range(6):
        users.append(
            User(
                email=f"reviewer{i+1}@bitescore.demo",
                hashed_password=get_password_hash(DEMO_PASSWORD),
                full_name=f"Reviewer {i+1}",
                role=UserRole.USER,
            )
        )
    db.add_all(users)
    db.flush()

    categories = [Category(name=n, slug=s) for n, s in CATEGORIES]
    db.add_all(categories)
    db.flush()

    business_types = list(BusinessType)
    businesses: list[Business] = []

    for i, name in enumerate(BUSINESS_NAMES):
        city_data = CITIES[i % len(CITIES)]
        cat = categories[i % len(categories)]
        btype = business_types[i % len(business_types)]
        business = Business(
            name=name,
            slug=slugify(name),
            category_id=cat.id,
            business_type=btype,
            description=f"{name} is a community-reviewed food business focused on hygiene transparency.",
            cover_image_url=cover_for_category(cat.slug),
            claimed_by_id=users[1].id if i == 0 else None,
        )
        db.add(business)
        db.flush()
        db.add(
            Location(
                business_id=business.id,
                address=f"{100 + i} Main Street",
                city=city_data["city"],
                country=city_data["country"],
                latitude=round(city_data["lat"] + random.uniform(-0.04, 0.04), 6),
                longitude=round(city_data["lng"] + random.uniform(-0.04, 0.04), 6),
            )
        )
        businesses.append(business)

    db.add(
        VerificationBadge(
            business_id=businesses[0].id, badge_type=BadgeType.CLAIMED, issued_by_id=users[0].id
        )
    )
    db.add(
        VerificationBadge(
            business_id=businesses[0].id, badge_type=BadgeType.VERIFIED, issued_by_id=users[0].id
        )
    )
    db.add(
        VerificationBadge(
            business_id=businesses[1].id,
            badge_type=BadgeType.HIGH_CONFIDENCE,
            issued_by_id=users[0].id,
        )
    )
    db.add(
        VerificationBadge(
            business_id=businesses[5].id,
            badge_type=BadgeType.UNDER_REVIEW,
            issued_by_id=users[0].id,
        )
    )

    db.add(
        ClaimRequest(
            business_id=businesses[2].id,
            user_id=users[1].id,
            status=ClaimStatus.PENDING,
            notes="I am the registered owner.",
        )
    )

    visit_types = list(VisitType)
    review_count = 0
    for _ in range(100):
        business = random.choice(businesses)
        user = random.choice(users[4:])
        days_ago = random.randint(1, 180)
        review = Review(
            business_id=business.id,
            user_id=user.id,
            visit_type=random.choice(visit_types),
            visit_date=date.today() - timedelta(days=days_ago),
            notes=random.choice(NOTES),
            consent_given=True,
            status=ReviewStatus.APPROVED,
            business_response="Thank you for your community observation."
            if random.random() < 0.2 and business.claimed_by_id
            else None,
        )
        db.add(review)
        db.flush()
        db.add(
            StructuredScore(
                review_id=review.id,
                cleanliness=round(random.uniform(2.5, 5.0), 1),
                staff_hygiene=round(random.uniform(2.5, 5.0), 1),
                food_handling=round(random.uniform(2.5, 5.0), 1),
                packaging=round(random.uniform(2.5, 5.0), 1),
                water_confidence=round(random.uniform(2.5, 5.0), 1),
                oil_freshness_concern=random.random() < 0.15,
                taste_optional=round(random.uniform(3.0, 5.0), 1)
                if random.random() < 0.5
                else None,
            )
        )
        review_count += 1
        if random.random() < 0.18:
            create_evidence_upload(db, review, verified=random.random() < 0.2)

    db.commit()
    db.close()
    print(f"Seeded {len(businesses)} businesses, {review_count} reviews, {len(users)} users.")
    print(f"Demo password for all accounts: {DEMO_PASSWORD}")


def main():
    seed()


if __name__ == "__main__":
    main()
