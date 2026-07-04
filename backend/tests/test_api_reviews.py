from tests.conftest import auth_header


def test_create_review_requires_auth(client, sample_business):
    response = client.post(
        "/reviews",
        json={
            "business_id": sample_business.id,
            "visit_type": "dine_in",
            "visit_date": "2026-02-01",
            "consent_given": True,
            "structured_score": {
                "cleanliness": 4,
                "staff_hygiene": 4,
                "food_handling": 4,
                "packaging": 4,
                "water_confidence": 4,
                "oil_freshness_concern": False,
            },
        },
    )
    assert response.status_code == 401


def test_create_review_requires_consent(client, test_user, sample_business):
    headers = auth_header(client, test_user.email, "Test1234!")
    response = client.post(
        "/reviews",
        headers=headers,
        json={
            "business_id": sample_business.id,
            "visit_type": "dine_in",
            "visit_date": "2026-02-01",
            "consent_given": False,
            "structured_score": {
                "cleanliness": 4,
                "staff_hygiene": 4,
                "food_handling": 4,
                "packaging": 4,
                "water_confidence": 4,
                "oil_freshness_concern": False,
            },
        },
    )
    assert response.status_code == 400


def test_create_review_success(client, test_user, sample_business):
    headers = auth_header(client, test_user.email, "Test1234!")
    response = client.post(
        "/reviews",
        headers=headers,
        json={
            "business_id": sample_business.id,
            "visit_type": "takeaway",
            "visit_date": "2026-02-01",
            "notes": "Community observation: packaging was secure.",
            "consent_given": True,
            "structured_score": {
                "cleanliness": 4.5,
                "staff_hygiene": 4.0,
                "food_handling": 4.5,
                "packaging": 5.0,
                "water_confidence": 4.0,
                "oil_freshness_concern": False,
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["visit_type"] == "takeaway"
    assert data["status"] == "pending"
    assert data["structured_score"]["packaging"] == 5.0


def test_pending_review_not_public_until_approved(client, test_user, sample_business):
    headers = auth_header(client, test_user.email, "Test1234!")
    payload = {
        "business_id": sample_business.id,
        "visit_type": "dine_in",
        "visit_date": "2026-03-01",
        "notes": "Pending moderation test.",
        "consent_given": True,
        "structured_score": {
            "cleanliness": 4,
            "staff_hygiene": 4,
            "food_handling": 4,
            "packaging": 4,
            "water_confidence": 4,
            "oil_freshness_concern": False,
        },
    }
    created = client.post("/reviews", headers=headers, json=payload)
    assert created.json()["status"] == "pending"

    public = client.get("/businesses/test-kitchen/reviews").json()
    assert all(review["id"] != created.json()["id"] for review in public)

    score = client.get("/businesses/test-kitchen").json()["score"]
    assert score["review_count"] == 0


def test_moderator_approval_publishes_review(client, test_user, admin_user, sample_business):
    headers = auth_header(client, test_user.email, "Test1234!")
    review = client.post(
        "/reviews",
        headers=headers,
        json={
            "business_id": sample_business.id,
            "visit_type": "dine_in",
            "visit_date": "2026-03-02",
            "consent_given": True,
            "structured_score": {
                "cleanliness": 4,
                "staff_hygiene": 4,
                "food_handling": 4,
                "packaging": 4,
                "water_confidence": 4,
                "oil_freshness_concern": False,
            },
        },
    ).json()

    mod_headers = auth_header(client, admin_user.email, "Test1234!")
    client.post(
        "/admin/moderate",
        headers=mod_headers,
        json={"action": "approve", "target_type": "review", "target_id": review["id"]},
    )

    public = client.get("/businesses/test-kitchen/reviews").json()
    assert any(item["id"] == review["id"] for item in public)


def test_my_reviews(client, test_user, sample_review):
    headers = auth_header(client, test_user.email, "Test1234!")
    response = client.get("/reviews/me", headers=headers)
    assert response.status_code == 200
    reviews = response.json()
    assert len(reviews) == 1
    assert reviews[0]["id"] == sample_review.id


def test_billing_status_mock(client):
    response = client.get("/billing/status")
    assert response.status_code == 200
    data = response.json()
    assert data["plan"] == "free"
    assert data["status"] == "active"
