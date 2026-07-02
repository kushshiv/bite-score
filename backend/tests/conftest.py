import os

os.environ.setdefault("GEOCODING_ENABLED", "false")

from collections.abc import Generator
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.migrate import run_migrations
from app.db.session import SessionLocal, engine, get_db
from app.main import app
from app.models.business import Business
from app.models.category import Category
from app.models.enums import BusinessType, ReviewStatus, UserRole, VisitType
from app.models.evidence_upload import EvidenceUpload
from app.models.location import Location
from app.models.review import Review
from app.models.structured_score import StructuredScore
from app.models.user import User


def reset_database() -> None:
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    run_migrations()


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    reset_database()
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        reset_database()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session) -> User:
    user = User(
        email="test@bitescore.demo",
        hashed_password=get_password_hash("Test1234!"),
        full_name="Test User",
        role=UserRole.USER,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session: Session) -> User:
    user = User(
        email="admin-test@bitescore.demo",
        hashed_password=get_password_hash("Test1234!"),
        full_name="Admin Test",
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def owner_user(db_session: Session) -> User:
    user = User(
        email="owner-test@bitescore.demo",
        hashed_password=get_password_hash("Test1234!"),
        full_name="Owner Test",
        role=UserRole.BUSINESS_OWNER,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def claimed_business(db_session: Session, owner_user: User, sample_business: Business) -> Business:
    sample_business.claimed_by_id = owner_user.id
    db_session.commit()
    db_session.refresh(sample_business)
    return sample_business


@pytest.fixture
def sample_business(db_session: Session) -> Business:
    category = Category(name="Test Cafe", slug="test-cafe")
    db_session.add(category)
    db_session.flush()

    business = Business(
        name="Test Kitchen",
        slug="test-kitchen",
        category_id=category.id,
        business_type=BusinessType.RESTAURANT,
        description="A test business",
    )
    db_session.add(business)
    db_session.flush()

    db_session.add(
        Location(
            business_id=business.id,
            address="1 Test Street",
            city="Berlin",
            country="Germany",
            latitude=52.52,
            longitude=13.405,
        )
    )
    db_session.commit()
    db_session.refresh(business)
    return business


@pytest.fixture
def sample_review(db_session: Session, test_user: User, sample_business: Business) -> Review:
    review = Review(
        business_id=sample_business.id,
        user_id=test_user.id,
        visit_type=VisitType.DINE_IN,
        visit_date=date(2026, 1, 15),
        notes="Clean dining area observed.",
        consent_given=True,
        status=ReviewStatus.APPROVED,
    )
    db_session.add(review)
    db_session.flush()
    db_session.add(
        StructuredScore(
            review_id=review.id,
            cleanliness=4.5,
            staff_hygiene=4.0,
            food_handling=4.5,
            packaging=4.0,
            water_confidence=4.5,
            oil_freshness_concern=False,
        )
    )
    db_session.commit()
    db_session.refresh(review)
    return review


@pytest.fixture
def sample_evidence(
    db_session: Session, sample_review: Review, sample_business: Business
) -> EvidenceUpload:
    upload = EvidenceUpload(
        review_id=sample_review.id,
        business_id=sample_business.id,
        file_path="uploads/test-evidence.jpg",
        mime_type="image/jpeg",
        verified=False,
    )
    db_session.add(upload)
    db_session.commit()
    db_session.refresh(upload)
    return upload


@pytest.fixture
def geo_businesses(db_session: Session) -> dict[str, Business]:
    """Three Berlin businesses at different distances from the city center."""
    category = Category(name="Geo Cafe", slug="geo-cafe")
    db_session.add(category)
    db_session.flush()

    configs = [
        ("Near Kitchen", "near-kitchen", 52.521, 13.406),
        ("Mid Kitchen", "mid-kitchen", 52.55, 13.405),
        ("Far Kitchen", "far-kitchen", 52.62, 13.405),
    ]
    businesses: dict[str, Business] = {}
    for name, slug, lat, lng in configs:
        business = Business(
            name=name,
            slug=slug,
            category_id=category.id,
            business_type=BusinessType.RESTAURANT,
            description=f"{name} for geo tests",
        )
        db_session.add(business)
        db_session.flush()
        db_session.add(
            Location(
                business_id=business.id,
                address=f"{slug} street",
                city="Berlin",
                country="Germany",
                latitude=lat,
                longitude=lng,
            )
        )
        businesses[slug] = business

    db_session.commit()
    for business in businesses.values():
        db_session.refresh(business)
    return businesses


def auth_header(client: TestClient, email: str, password: str) -> dict[str, str]:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
