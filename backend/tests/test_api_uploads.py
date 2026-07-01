from app.models.admin_audit import AdminAudit
from app.models.evidence_upload import EvidenceUpload
from tests.conftest import auth_header


class TestVerifyEvidence:
    def test_requires_moderator(self, client, sample_evidence, test_user):
        headers = auth_header(client, test_user.email, "Test1234!")
        response = client.patch(f"/uploads/{sample_evidence.id}/verify", headers=headers)
        assert response.status_code == 403

    def test_verifies_upload(self, client, sample_evidence, admin_user):
        headers = auth_header(client, admin_user.email, "Test1234!")
        response = client.patch(f"/uploads/{sample_evidence.id}/verify", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["verified"] is True
        assert data["id"] == sample_evidence.id

    def test_verify_is_idempotent(self, client, sample_evidence, admin_user):
        headers = auth_header(client, admin_user.email, "Test1234!")
        first = client.patch(f"/uploads/{sample_evidence.id}/verify", headers=headers)
        second = client.patch(f"/uploads/{sample_evidence.id}/verify", headers=headers)
        assert first.status_code == 200
        assert second.status_code == 200
        assert second.json()["verified"] is True

    def test_records_audit(self, client, db_session, sample_evidence, admin_user):
        headers = auth_header(client, admin_user.email, "Test1234!")
        client.patch(f"/uploads/{sample_evidence.id}/verify", headers=headers)
        audit = (
            db_session.query(AdminAudit)
            .filter(
                AdminAudit.action == "verify_evidence",
                AdminAudit.target_id == sample_evidence.id,
            )
            .first()
        )
        assert audit is not None
        assert audit.actor_id == admin_user.id

    def test_not_found(self, client, admin_user):
        headers = auth_header(client, admin_user.email, "Test1234!")
        response = client.patch("/uploads/99999/verify", headers=headers)
        assert response.status_code == 404


class TestModerationQueueEvidence:
    def test_lists_unverified_evidence(self, client, sample_evidence, admin_user):
        headers = auth_header(client, admin_user.email, "Test1234!")
        data = client.get("/admin/moderation-queue", headers=headers).json()
        assert data["pending_evidence"] == 1
        assert len(data["evidence"]) == 1
        assert data["evidence"][0]["id"] == sample_evidence.id
        assert data["evidence"][0]["business_slug"] == "test-kitchen"
        assert data["evidence"][0]["verified"] is False

    def test_excludes_verified_evidence(self, client, sample_evidence, admin_user):
        headers = auth_header(client, admin_user.email, "Test1234!")
        client.patch(f"/uploads/{sample_evidence.id}/verify", headers=headers)
        data = client.get("/admin/moderation-queue", headers=headers).json()
        assert data["pending_evidence"] == 0
        assert data["evidence"] == []
