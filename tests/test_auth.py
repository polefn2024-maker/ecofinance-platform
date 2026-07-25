"""Tests for authentication endpoints."""


def test_register_success(client):
    resp = client.post("/api/auth/register", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "Password1!",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["user"]["username"] == "alice"
    assert "access_token" in data


def test_register_duplicate_username(client):
    payload = {"username": "bob", "email": "bob@example.com", "password": "P@ss1"}
    client.post("/api/auth/register", json=payload)
    resp = client.post("/api/auth/register", json={
        "username": "bob",
        "email": "bob2@example.com",
        "password": "P@ss1",
    })
    assert resp.status_code == 409


def test_register_duplicate_email(client):
    client.post("/api/auth/register", json={
        "username": "carol1",
        "email": "carol@example.com",
        "password": "P@ss1",
    })
    resp = client.post("/api/auth/register", json={
        "username": "carol2",
        "email": "carol@example.com",
        "password": "P@ss1",
    })
    assert resp.status_code == 409


def test_register_missing_fields(client):
    resp = client.post("/api/auth/register", json={"username": "dave"})
    assert resp.status_code == 400


def test_login_success(client):
    client.post("/api/auth/register", json={
        "username": "eve",
        "email": "eve@example.com",
        "password": "P@ss1",
    })
    resp = client.post("/api/auth/login", json={
        "email": "eve@example.com",
        "password": "P@ss1",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "username": "frank",
        "email": "frank@example.com",
        "password": "correct",
    })
    resp = client.post("/api/auth/login", json={
        "email": "frank@example.com",
        "password": "wrong",
    })
    assert resp.status_code == 401


def test_profile_requires_auth(client):
    resp = client.get("/api/auth/profile")
    assert resp.status_code == 401


def test_profile_returns_user(client, auth_headers):
    resp = client.get("/api/auth/profile", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["email"] == "test@ecofinance.com"


def test_update_profile(client, auth_headers):
    resp = client.put("/api/auth/profile", headers=auth_headers, json={
        "full_name": "Updated Name",
        "country": "Kenya",
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["full_name"] == "Updated Name"
    assert data["country"] == "Kenya"
