from datetime import date

from app.models.enums import ReviewStatus, VisitType
from app.models.review import Review
from tests.conftest import auth_header


class TestRespondToReview:
    def test_requires_auth(self, client, sample_review):
        response = client.patch(
            f"/business-dashboard/reviews/{sample_review.id}/respond",
            json={"response": "Thank you for your observation."},
        )
        assert response.status_code == 401

    def test_requires_claimed_business(self, client, test_user, sample_review):
        headers = auth_header(client, test_user.email, "Test1234!")
        response = client.patch(
            f"/business-dashboard/reviews/{sample_review.id}/respond",
            headers=headers,
            json={"response": "Thank you for your observation."},
        )
        assert response.status_code == 404

    def test_posts_response(self, client, owner_user, claimed_business, sample_review):
        headers = auth_header(client, owner_user.email, "Test1234!")
        response = client.patch(
            f"/business-dashboard/reviews/{sample_review.id}/respond",
            headers=headers,
            json={"response": "Thank you for sharing your community observation."},
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Response posted"

        public = client.get("/businesses/test-kitchen/reviews").json()
        assert public[0]["business_response"] == "Thank you for sharing your community observation."

    def test_validates_min_length(self, client, owner_user, claimed_business, sample_review):
        headers = auth_header(client, owner_user.email, "Test1234!")
        response = client.patch(
            f"/business-dashboard/reviews/{sample_review.id}/respond",
            headers=headers,
            json={"response": "Too short"},
        )
        assert response.status_code == 422

    def test_cannot_respond_to_other_business_review(
        self, client, db_session, owner_user, claimed_business, test_user, geo_businesses
    ):
        other_business = geo_businesses["far-kitchen"]
        other_review = Review(
            business_id=other_business.id,
            user_id=test_user.id,
            visit_type=VisitType.DINE_IN,
            visit_date=date(2026, 2, 1),
            consent_given=True,
            status=ReviewStatus.APPROVED,
        )
        db_session.add(other_review)
        db_session.commit()
        db_session.refresh(other_review)

        headers = auth_header(client, owner_user.email, "Test1234!")
        response = client.patch(
            f"/business-dashboard/reviews/{other_review.id}/respond",
            headers=headers,
            json={"response": "This should not be allowed for another business."},
        )
        assert response.status_code == 404


class TestBusinessAccount:
    def test_returns_claimed_business(self, client, owner_user, claimed_business):
        headers = auth_header(client, owner_user.email, "Test1234!")
        data = client.get("/business-dashboard/account", headers=headers).json()
        assert data["claimed_business"]["slug"] == "test-kitchen"
        assert data["claimed_business"]["name"] == "Test Kitchen"

    def test_returns_empty_when_unclaimed(self, client, test_user):
        headers = auth_header(client, test_user.email, "Test1234!")
        data = client.get("/business-dashboard/account", headers=headers).json()
        assert data["claimed_business"] is None


class TestCreateClaim:
    def test_blocks_duplicate_pending_claim(self, client, db_session, test_user, sample_business):
        from app.models.claim_request import ClaimRequest
        from app.models.enums import ClaimStatus

        db_session.add(
            ClaimRequest(
                business_id=sample_business.id,
                user_id=test_user.id,
                status=ClaimStatus.PENDING,
                notes="First claim",
            )
        )
        db_session.commit()

        headers = auth_header(client, test_user.email, "Test1234!")
        response = client.post(
            "/claims",
            headers=headers,
            json={"business_id": sample_business.id, "notes": "Duplicate claim"},
        )
        assert response.status_code == 400

    def test_blocks_claim_when_already_managing_business(
        self, client, owner_user, claimed_business, sample_business
    ):
        headers = auth_header(client, owner_user.email, "Test1234!")
        response = client.post(
            "/claims",
            headers=headers,
            json={"business_id": sample_business.id, "notes": "Another claim"},
        )
        assert response.status_code == 400


class TestScoreTrend:
    def test_requires_claimed_business(self, client, test_user):
        headers = auth_header(client, test_user.email, "Test1234!")
        response = client.get("/business-dashboard/score-trend", headers=headers)
        assert response.status_code == 404

    def test_returns_trend_points(self, client, owner_user, claimed_business, sample_review):
        headers = auth_header(client, owner_user.email, "Test1234!")
        data = client.get("/business-dashboard/score-trend", headers=headers).json()
        assert data["weeks"] == 12
        assert len(data["points"]) >= 1
        assert data["points"][-1]["review_count"] >= 1
