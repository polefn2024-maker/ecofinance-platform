import pytest
from app import create_app, db


@pytest.fixture
def app():
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-jwt-secret-key-at-least-32-bytes-long",
        "SECRET_KEY": "test-secret",
    }
    application = create_app(test_config)
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Register a test user and return JWT auth headers."""
    client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@ecofinance.com",
        "password": "SecurePass123",
        "full_name": "Test User",
        "country": "Nigeria",
        "base_currency": "NGN",
    })
    resp = client.post("/api/auth/login", json={
        "email": "test@ecofinance.com",
        "password": "SecurePass123",
    })
    token = resp.get_json()["access_token"]
    scheme = "Bearer"
    return {"Authorization": f"{scheme} {token}"}
