

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


def test_get_business_by_slug(client, sample_business, sample_review):
    response = client.get("/businesses/test-kitchen")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Kitchen"
    assert data["location"]["city"] == "Berlin"
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
