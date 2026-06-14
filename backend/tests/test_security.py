from app.core.security import create_access_token, decode_access_token, get_password_hash, verify_password


def test_password_hash_and_verify():
    password = "SecurePass123!"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)


def test_create_and_decode_access_token():
    token = create_access_token("user@bitescore.demo", "user")
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "user@bitescore.demo"
    assert payload["role"] == "user"


def test_decode_invalid_token_returns_none():
    assert decode_access_token("not-a-valid-token") is None
