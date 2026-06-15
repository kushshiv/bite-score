

from app.models.business import Business
from app.models.category import Category
from app.models.enums import BusinessType
from app.models.location import Location


def test_list_businesses_empty(client):
    response = client.get("/businesses")
    assert response.status_code == 200
    assert response.json() == []


def test_list_businesses_with_data(client, sample_business):
    response = client.get("/businesses")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Kitchen"
    assert data[0]["slug"] == "test-kitchen"
    assert data[0]["review_count"] == 0
    assert data[0]["distance_km"] is None


def test_list_businesses_includes_review_count(client, sample_business, sample_review):
    response = client.get("/businesses")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["review_count"] == 1
    assert data[0]["overall_percent"] > 0


def test_get_business_by_slug(client, sample_business, sample_review):
    response = client.get("/businesses/test-kitchen")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Kitchen"
    assert data["location"]["city"] == "Berlin"
    assert data["location"]["latitude"] == 52.52
    assert data["location"]["longitude"] == 13.405
    assert data["review_count"] == 1
    assert data["score"]["review_count"] == 1
    assert data["score"]["overall"] > 0


def test_get_business_not_found(client):
    response = client.get("/businesses/does-not-exist")
    assert response.status_code == 404


def test_search_businesses_by_city(client, sample_business):
    response = client.get("/businesses", params={"city": "Berlin"})
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = client.get("/businesses", params={"city": "Mumbai"})
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_business_reviews(client, sample_business, sample_review):
    response = client.get("/businesses/test-kitchen/reviews")
    assert response.status_code == 200
    reviews = response.json()
    assert len(reviews) == 1
    assert reviews[0]["notes"] == "Clean dining area observed."


def test_list_businesses_nearby_includes_distance(client, geo_businesses):
    response = client.get(
        "/businesses",
        params={
            "city": "Berlin",
            "near_lat": 52.52,
            "near_lng": 13.405,
            "sort": "nearby",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(item["distance_km"] is not None for item in data)
    assert data[0]["slug"] == "near-kitchen"
    assert data[0]["distance_km"] < data[1]["distance_km"] < data[2]["distance_km"]


def test_list_businesses_nearby_respects_radius(client, geo_businesses):
    response = client.get(
        "/businesses",
        params={
            "city": "Berlin",
            "near_lat": 52.52,
            "near_lng": 13.405,
            "radius_km": 5,
            "sort": "nearby",
        },
    )
    assert response.status_code == 200
    data = response.json()
    slugs = {item["slug"] for item in data}
    assert "near-kitchen" in slugs
    assert "mid-kitchen" in slugs
    assert "far-kitchen" not in slugs


def test_list_businesses_nearby_sort_by_score(client, geo_businesses, db_session, test_user):
    from datetime import date

    from app.models.enums import ReviewStatus, VisitType
    from app.models.review import Review
    from app.models.structured_score import StructuredScore

    far = geo_businesses["far-kitchen"]
    review = Review(
        business_id=far.id,
        user_id=test_user.id,
        visit_type=VisitType.DINE_IN,
        visit_date=date(2026, 2, 1),
        notes="Excellent hygiene.",
        consent_given=True,
        status=ReviewStatus.APPROVED,
    )
    db_session.add(review)
    db_session.flush()
    db_session.add(
        StructuredScore(
            review_id=review.id,
            cleanliness=5.0,
            staff_hygiene=5.0,
            food_handling=5.0,
            packaging=5.0,
            water_confidence=5.0,
            oil_freshness_concern=False,
        )
    )
    db_session.commit()

    response = client.get(
        "/businesses",
        params={
            "city": "Berlin",
            "near_lat": 52.52,
            "near_lng": 13.405,
            "sort": "score",
            "limit": 3,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["slug"] == "far-kitchen"
    assert data[0]["overall_percent"] >= data[1]["overall_percent"]


def test_list_businesses_nearby_excludes_missing_coordinates(client, db_session):
    category = Category(name="No Geo", slug="no-geo")
    db_session.add(category)
    db_session.flush()

    business = Business(
        name="No Coords Kitchen",
        slug="no-coords-kitchen",
        category_id=category.id,
        business_type=BusinessType.RESTAURANT,
        description="Missing coordinates",
    )
    db_session.add(business)
    db_session.flush()
    db_session.add(
        Location(
            business_id=business.id,
            address="Unknown",
            city="Berlin",
            country="Germany",
        )
    )
    db_session.commit()

    response = client.get(
        "/businesses",
        params={
            "city": "Berlin",
            "near_lat": 52.52,
            "near_lng": 13.405,
        },
    )
    assert response.status_code == 200
    assert response.json() == []


def test_list_businesses_sort_score_without_geo(client, geo_businesses, db_session, test_user):
    from datetime import date

    from app.models.enums import ReviewStatus, VisitType
    from app.models.review import Review
    from app.models.structured_score import StructuredScore

    near = geo_businesses["near-kitchen"]
    review = Review(
        business_id=near.id,
        user_id=test_user.id,
        visit_type=VisitType.DINE_IN,
        visit_date=date(2026, 2, 1),
        notes="Great place.",
        consent_given=True,
        status=ReviewStatus.APPROVED,
    )
    db_session.add(review)
    db_session.flush()
    db_session.add(
        StructuredScore(
            review_id=review.id,
            cleanliness=5.0,
            staff_hygiene=5.0,
            food_handling=5.0,
            packaging=5.0,
            water_confidence=5.0,
            oil_freshness_concern=False,
        )
    )
    db_session.commit()

    response = client.get("/businesses", params={"city": "Berlin", "sort": "score"})
    assert response.status_code == 200
    data = response.json()
    assert data[0]["slug"] == "near-kitchen"
    assert data[0]["overall_percent"] > 0
