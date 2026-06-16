from datetime import date

from app.models.business import Business
from app.models.category import Category
from app.models.enums import BadgeType, BusinessType, ReviewStatus, VisitType
from app.models.location import Location
from app.models.review import Review
from app.models.structured_score import StructuredScore
from app.models.verification_badge import VerificationBadge


class TestListBusinesses:
    def test_empty(self, client):
        response = client.get("/businesses")
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_core_fields(self, client, sample_business):
        response = client.get("/businesses")
        data = response.json()
        assert len(data) == 1
        item = data[0]
        assert item["name"] == "Test Kitchen"
        assert item["slug"] == "test-kitchen"
        assert item["review_count"] == 0
        assert item["distance_km"] is None
        assert item["cover_image_url"] is None

    def test_includes_review_count(self, client, sample_business, sample_review):
        data = client.get("/businesses").json()
        assert data[0]["review_count"] == 1
        assert data[0]["overall_percent"] > 0

    def test_includes_cover_image(self, client, sample_business, db_session):
        sample_business.cover_image_url = "https://images.unsplash.com/photo-example"
        db_session.commit()
        assert (
            client.get("/businesses").json()[0]["cover_image_url"]
            == "https://images.unsplash.com/photo-example"
        )

    def test_filter_by_city(self, client, sample_business):
        assert len(client.get("/businesses", params={"city": "Berlin"}).json()) == 1
        assert len(client.get("/businesses", params={"city": "Mumbai"}).json()) == 0

    def test_search_by_name(self, client, sample_business):
        assert len(client.get("/businesses", params={"q": "Test Kitchen"}).json()) == 1
        assert len(client.get("/businesses", params={"q": "missing"}).json()) == 0

    def test_filter_by_category(self, client, sample_business):
        assert len(client.get("/businesses", params={"category": "test-cafe"}).json()) == 1
        assert len(client.get("/businesses", params={"category": "indian"}).json()) == 0

    def test_high_trust_filter(self, client, sample_business, sample_review):
        assert len(client.get("/businesses", params={"high_trust": True}).json()) == 1

    def test_sort_by_score_without_geo(self, client, geo_businesses, db_session, test_user):
        near = geo_businesses["near-kitchen"]
        self._add_high_score_review(db_session, near.id, test_user.id)
        data = client.get("/businesses", params={"city": "Berlin", "sort": "score"}).json()
        assert data[0]["slug"] == "near-kitchen"
        assert data[0]["overall_percent"] > 0

    @staticmethod
    def _add_high_score_review(db_session, business_id, user_id):
        review = Review(
            business_id=business_id,
            user_id=user_id,
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


class TestNearbyBusinesses:
    def test_includes_distance_and_sorts_nearest_first(self, client, geo_businesses):
        data = client.get(
            "/businesses",
            params={"city": "Berlin", "near_lat": 52.52, "near_lng": 13.405, "sort": "nearby"},
        ).json()
        assert len(data) == 3
        assert all(item["distance_km"] is not None for item in data)
        assert data[0]["slug"] == "near-kitchen"
        assert data[0]["distance_km"] < data[1]["distance_km"] < data[2]["distance_km"]

    def test_respects_radius(self, client, geo_businesses):
        slugs = {
            item["slug"]
            for item in client.get(
                "/businesses",
                params={
                    "city": "Berlin",
                    "near_lat": 52.52,
                    "near_lng": 13.405,
                    "radius_km": 5,
                    "sort": "nearby",
                },
            ).json()
        }
        assert slugs == {"near-kitchen", "mid-kitchen"}

    def test_sort_by_score_within_geo(self, client, geo_businesses, db_session, test_user):
        far = geo_businesses["far-kitchen"]
        TestListBusinesses._add_high_score_review(db_session, far.id, test_user.id)
        data = client.get(
            "/businesses",
            params={
                "city": "Berlin",
                "near_lat": 52.52,
                "near_lng": 13.405,
                "sort": "score",
                "limit": 3,
            },
        ).json()
        assert data[0]["slug"] == "far-kitchen"

    def test_excludes_missing_coordinates(self, client, db_session):
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
        assert (
            client.get(
                "/businesses",
                params={"city": "Berlin", "near_lat": 52.52, "near_lng": 13.405},
            ).json()
            == []
        )


class TestBusinessFacets:
    def test_returns_counts_for_area(self, client, geo_businesses, db_session, test_user):
        near = geo_businesses["near-kitchen"]
        db_session.add(
            VerificationBadge(
                business_id=near.id, badge_type=BadgeType.VERIFIED, issued_by_id=test_user.id
            )
        )
        TestListBusinesses._add_high_score_review(db_session, near.id, test_user.id)

        data = client.get(
            "/businesses/facets",
            params={"city": "Berlin", "near_lat": 52.52, "near_lng": 13.405},
        ).json()

        assert data["total"] == 3
        assert data["verified"] >= 1
        assert data["high_trust"] >= 1
        assert data["safe_to_eat"] >= 1
        assert data["categories"] == [{"slug": "geo-cafe", "name": "Geo Cafe", "count": 3}]

    def test_respects_radius(self, client, geo_businesses):
        data = client.get(
            "/businesses/facets",
            params={
                "city": "Berlin",
                "near_lat": 52.52,
                "near_lng": 13.405,
                "radius_km": 5,
            },
        ).json()
        assert data["total"] == 2

    def test_search_narrows_facets(self, client, geo_businesses):
        data = client.get(
            "/businesses/facets",
            params={
                "city": "Berlin",
                "near_lat": 52.52,
                "near_lng": 13.405,
                "q": "Near",
            },
        ).json()
        assert data["total"] == 1
        assert data["categories"][0]["count"] == 1


class TestBusinessDetail:
    def test_get_by_slug(self, client, sample_business, sample_review):
        data = client.get("/businesses/test-kitchen").json()
        assert data["name"] == "Test Kitchen"
        assert data["location"]["city"] == "Berlin"
        assert data["location"]["latitude"] == 52.52
        assert data["location"]["longitude"] == 13.405
        assert data["review_count"] == 1
        assert data["score"]["review_count"] == 1
        assert data["score"]["overall"] > 0

    def test_not_found(self, client):
        assert client.get("/businesses/does-not-exist").status_code == 404

    def test_reviews(self, client, sample_business, sample_review):
        reviews = client.get("/businesses/test-kitchen/reviews").json()
        assert len(reviews) == 1
        assert reviews[0]["notes"] == "Clean dining area observed."
