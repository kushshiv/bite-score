from app.models.enums import BadgeType, ClaimStatus
from app.models.verification_badge import VerificationBadge
from tests.conftest import auth_header


class TestBadgeRequests:
    def test_requires_auth(self, client):
        response = client.post(
            "/business-dashboard/badge-requests",
            json={"notes": "We have FSSAI certification on file."},
        )
        assert response.status_code == 401

    def test_requires_claimed_business(self, client, test_user):
        headers = auth_header(client, test_user.email, "Test1234!")
        response = client.post(
            "/business-dashboard/badge-requests",
            headers=headers,
            json={"notes": "Please verify our kitchen."},
        )
        assert response.status_code == 404

    def test_create_and_list(self, client, owner_user, claimed_business):
        headers = auth_header(client, owner_user.email, "Test1234!")
        create = client.post(
            "/business-dashboard/badge-requests",
            headers=headers,
            json={"notes": "We maintain daily hygiene logs and staff training."},
        )
        assert create.status_code == 200
        body = create.json()
        assert body["badge_type"] == BadgeType.VERIFIED.value
        assert body["status"] == ClaimStatus.PENDING.value

        listed = client.get("/business-dashboard/badge-requests", headers=headers).json()
        assert listed["has_verified_badge"] is False
        assert len(listed["requests"]) == 1
        assert listed["requests"][0]["notes"].startswith("We maintain")

    def test_blocks_duplicate_pending(self, client, owner_user, claimed_business):
        headers = auth_header(client, owner_user.email, "Test1234!")
        client.post(
            "/business-dashboard/badge-requests",
            headers=headers,
            json={"notes": "First request"},
        )
        duplicate = client.post(
            "/business-dashboard/badge-requests",
            headers=headers,
            json={"notes": "Second request"},
        )
        assert duplicate.status_code == 400

    def test_blocks_when_already_verified(self, client, db_session, owner_user, claimed_business):
        db_session.add(
            VerificationBadge(
                business_id=claimed_business.id,
                badge_type=BadgeType.VERIFIED,
                issued_by_id=owner_user.id,
            )
        )
        db_session.commit()

        headers = auth_header(client, owner_user.email, "Test1234!")
        response = client.post(
            "/business-dashboard/badge-requests",
            headers=headers,
            json={"notes": "We would like verification."},
        )
        assert response.status_code == 400

        listed = client.get("/business-dashboard/badge-requests", headers=headers).json()
        assert listed["has_verified_badge"] is True


class TestBadgeRequestModeration:
    def test_pending_in_queue(self, client, owner_user, claimed_business, admin_user):
        owner_headers = auth_header(client, owner_user.email, "Test1234!")
        client.post(
            "/business-dashboard/badge-requests",
            headers=owner_headers,
            json={"notes": "Ready for official verification."},
        )

        admin_headers = auth_header(client, admin_user.email, "Test1234!")
        queue = client.get("/admin/moderation-queue", headers=admin_headers).json()
        assert queue["pending_badge_requests"] == 1
        assert queue["badge_requests"][0]["business_slug"] == claimed_business.slug

    def test_approve_issues_badge(self, client, owner_user, claimed_business, admin_user):
        owner_headers = auth_header(client, owner_user.email, "Test1234!")
        request_id = client.post(
            "/business-dashboard/badge-requests",
            headers=owner_headers,
            json={"notes": "Please review our profile."},
        ).json()["id"]

        admin_headers = auth_header(client, admin_user.email, "Test1234!")
        client.post(
            "/admin/moderate",
            headers=admin_headers,
            json={"action": "approve", "target_type": "badge_request", "target_id": request_id},
        )

        listed = client.get("/business-dashboard/badge-requests", headers=owner_headers).json()
        assert listed["has_verified_badge"] is True
        assert listed["requests"][0]["status"] == ClaimStatus.APPROVED.value

        profile = client.get(f"/businesses/{claimed_business.slug}").json()
        assert any(b["badge_type"] == BadgeType.VERIFIED.value for b in profile["badges"])

    def test_reject_leaves_badge_unassigned(self, client, owner_user, claimed_business, admin_user):
        owner_headers = auth_header(client, owner_user.email, "Test1234!")
        request_id = client.post(
            "/business-dashboard/badge-requests",
            headers=owner_headers,
            json={"notes": "Needs more evidence."},
        ).json()["id"]

        admin_headers = auth_header(client, admin_user.email, "Test1234!")
        client.post(
            "/admin/moderate",
            headers=admin_headers,
            json={"action": "reject", "target_type": "badge_request", "target_id": request_id},
        )

        listed = client.get("/business-dashboard/badge-requests", headers=owner_headers).json()
        assert listed["has_verified_badge"] is False
        assert listed["requests"][0]["status"] == ClaimStatus.REJECTED.value

        queue = client.get("/admin/moderation-queue", headers=admin_headers).json()
        assert queue["pending_badge_requests"] == 0
