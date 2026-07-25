"""Tests for currency endpoints."""


def test_list_currencies(client):
    resp = client.get("/api/currencies/")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    codes = [c["code"] for c in data]
    assert "NGN" in codes
    assert "KES" in codes
    assert "ZAR" in codes


def test_get_currency(client):
    resp = client.get("/api/currencies/NGN")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["code"] == "NGN"
    assert data["name"] == "Nigerian Naira"


def test_get_currency_case_insensitive(client):
    resp = client.get("/api/currencies/ngn")
    assert resp.status_code == 200
    assert resp.get_json()["code"] == "NGN"


def test_get_unknown_currency(client):
    resp = client.get("/api/currencies/XYZ")
    assert resp.status_code == 404


def test_convert_requires_auth(client):
    resp = client.get("/api/currencies/convert?from=NGN&to=USD&amount=1000")
    assert resp.status_code == 401


def test_convert(client, auth_headers):
    resp = client.get(
        "/api/currencies/convert?from=USD&to=NGN&amount=1",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["from"] == "USD"
    assert data["to"] == "NGN"
    assert data["converted"] > 0


def test_convert_missing_params(client, auth_headers):
    resp = client.get("/api/currencies/convert?from=NGN&amount=100", headers=auth_headers)
    assert resp.status_code == 400


def test_convert_invalid_amount(client, auth_headers):
    resp = client.get("/api/currencies/convert?from=NGN&to=USD&amount=-1", headers=auth_headers)
    assert resp.status_code == 400


def test_update_rate(client, auth_headers):
    resp = client.put("/api/currencies/NGN/rate", headers=auth_headers, json={"usd_rate": 1600.0})
    assert resp.status_code == 200
    assert resp.get_json()["usd_rate"] == 1600.0
