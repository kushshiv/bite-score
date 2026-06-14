from tests.conftest import auth_header


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_and_login(client):
    register = client.post(
        "/auth/register",
        json={"email": "newuser@bitescore.demo", "password": "Test1234!", "full_name": "New User"},
    )
    assert register.status_code == 200
    assert "access_token" in register.json()

    login = client.post("/auth/login", json={"email": "newuser@bitescore.demo", "password": "Test1234!"})
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"


def test_login_invalid_credentials(client, test_user):
    response = client.post("/auth/login", json={"email": test_user.email, "password": "WrongPass!"})
    assert response.status_code == 401


def test_register_duplicate_email(client, test_user):
    response = client.post(
        "/auth/register",
        json={"email": test_user.email, "password": "Test1234!"},
    )
    assert response.status_code == 400


def test_me_requires_auth(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_me_returns_user(client, test_user):
    headers = auth_header(client, test_user.email, "Test1234!")
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["role"] == "user"
