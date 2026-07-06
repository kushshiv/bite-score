import io

from PIL import Image

from app.models.enums import BadgeType, CertificationStatus
from tests.conftest import auth_header


def _png_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), color="red").save(buf, format="PNG")
    return buf.getvalue()


class TestCertificationUploads:
    def test_requires_auth(self, client):
        response = client.post(
            "/business-dashboard/certifications",
            data={"title": "FSSAI License"},
            files={"file": ("cert.png", _png_bytes(), "image/png")},
        )
        assert response.status_code == 401

    def test_requires_claimed_business(self, client, test_user):
        headers = auth_header(client, test_user.email, "Test1234!")
        response = client.post(
            "/business-dashboard/certifications",
            headers=headers,
            data={"title": "FSSAI License"},
            files={"file": ("cert.png", _png_bytes(), "image/png")},
        )
        assert response.status_code == 404

    def test_upload_and_list(self, client, owner_user, claimed_business):
        headers = auth_header(client, owner_user.email, "Test1234!")
        upload = client.post(
            "/business-dashboard/certifications",
            headers=headers,
            data={"title": "FSSAI License 2026"},
            files={"file": ("cert.png", _png_bytes(), "image/png")},
        )
        assert upload.status_code == 200
        body = upload.json()
        assert body["title"] == "FSSAI License 2026"
        assert body["status"] == "pending"
        assert body["mime_type"] == "image/png"
        assert body["file_url"].endswith(".png")

        listed = client.get("/business-dashboard/certifications", headers=headers).json()
        assert len(listed["certifications"]) == 1
        assert listed["certifications"][0]["id"] == body["id"]

    def test_validates_title(self, client, owner_user, claimed_business):
        headers = auth_header(client, owner_user.email, "Test1234!")
        response = client.post(
            "/business-dashboard/certifications",
            headers=headers,
            data={"title": "ab"},
            files={"file": ("cert.png", _png_bytes(), "image/png")},
        )
        assert response.status_code == 400

    def test_accepts_pdf(self, client, owner_user, claimed_business):
        headers = auth_header(client, owner_user.email, "Test1234!")
        pdf = b"%PDF-1.4 minimal test content"
        response = client.post(
            "/business-dashboard/certifications",
            headers=headers,
            data={"title": "Health inspection report"},
            files={"file": ("report.pdf", pdf, "application/pdf")},
        )
        assert response.status_code == 200
        assert response.json()["mime_type"] == "application/pdf"


class TestCertificationModeration:
    def test_pending_in_queue(self, client, owner_user, claimed_business, admin_user):
        owner_headers = auth_header(client, owner_user.email, "Test1234!")
        client.post(
            "/business-dashboard/certifications",
            headers=owner_headers,
            data={"title": "Kitchen hygiene certificate"},
            files={"file": ("cert.png", _png_bytes(), "image/png")},
        )

        mod_headers = auth_header(client, admin_user.email, "Test1234!")
        queue = client.get("/admin/moderation-queue", headers=mod_headers).json()
        assert queue["pending_certifications"] == 1
        assert len(queue["certifications"]) == 1
        assert queue["certifications"][0]["title"] == "Kitchen hygiene certificate"

    def test_moderator_approves(self, client, owner_user, claimed_business, admin_user):
        owner_headers = auth_header(client, owner_user.email, "Test1234!")
        cert_id = client.post(
            "/business-dashboard/certifications",
            headers=owner_headers,
            data={"title": "ISO 22000"},
            files={"file": ("cert.png", _png_bytes(), "image/png")},
        ).json()["id"]

        mod_headers = auth_header(client, admin_user.email, "Test1234!")
        moderate = client.post(
            "/admin/moderate",
            headers=mod_headers,
            json={"action": "approve", "target_type": "certification", "target_id": cert_id},
        )
        assert moderate.status_code == 200

        listed = client.get("/business-dashboard/certifications", headers=owner_headers).json()
        assert listed["certifications"][0]["status"] == CertificationStatus.VERIFIED.value
        assert listed["has_verified_badge"] is True

        profile = client.get(f"/businesses/{claimed_business.slug}").json()
        assert any(b["badge_type"] == BadgeType.VERIFIED.value for b in profile["badges"])

    def test_moderator_rejects(self, client, owner_user, claimed_business, admin_user):
        owner_headers = auth_header(client, owner_user.email, "Test1234!")
        cert_id = client.post(
            "/business-dashboard/certifications",
            headers=owner_headers,
            data={"title": "Expired permit"},
            files={"file": ("cert.png", _png_bytes(), "image/png")},
        ).json()["id"]

        mod_headers = auth_header(client, admin_user.email, "Test1234!")
        client.post(
            "/admin/moderate",
            headers=mod_headers,
            json={"action": "reject", "target_type": "certification", "target_id": cert_id},
        )

        listed = client.get("/business-dashboard/certifications", headers=owner_headers).json()
        assert listed["certifications"][0]["status"] == CertificationStatus.REJECTED.value
        assert listed["has_verified_badge"] is False

        queue = client.get("/admin/moderation-queue", headers=mod_headers).json()
        assert queue["pending_certifications"] == 0
