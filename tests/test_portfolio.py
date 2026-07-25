"""Tests for portfolio and asset endpoints."""


def test_list_portfolios_empty(client, auth_headers):
    resp = client.get("/api/portfolio/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_portfolio(client, auth_headers):
    resp = client.post("/api/portfolio/", headers=auth_headers, json={
        "name": "NSE Portfolio",
        "description": "Nigerian Stock Exchange holdings",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "NSE Portfolio"


def test_create_portfolio_no_name(client, auth_headers):
    resp = client.post("/api/portfolio/", headers=auth_headers, json={
        "description": "Missing name",
    })
    assert resp.status_code == 400


def test_get_portfolio(client, auth_headers):
    create_resp = client.post("/api/portfolio/", headers=auth_headers, json={"name": "Test"})
    pid = create_resp.get_json()["id"]
    resp = client.get(f"/api/portfolio/{pid}", headers=auth_headers)
    assert resp.status_code == 200
    assert "assets" in resp.get_json()


def test_update_portfolio(client, auth_headers):
    create_resp = client.post("/api/portfolio/", headers=auth_headers, json={"name": "Old"})
    pid = create_resp.get_json()["id"]
    resp = client.put(f"/api/portfolio/{pid}", headers=auth_headers, json={"name": "New"})
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "New"


def test_delete_portfolio(client, auth_headers):
    create_resp = client.post("/api/portfolio/", headers=auth_headers, json={"name": "Delete Me"})
    pid = create_resp.get_json()["id"]
    resp = client.delete(f"/api/portfolio/{pid}", headers=auth_headers)
    assert resp.status_code == 200
    assert client.get(f"/api/portfolio/{pid}", headers=auth_headers).status_code == 404


def test_add_asset_to_portfolio(client, auth_headers):
    pid = client.post("/api/portfolio/", headers=auth_headers, json={"name": "P1"}).get_json()["id"]
    resp = client.post(f"/api/portfolio/{pid}/assets", headers=auth_headers, json={
        "name": "Dangote Cement",
        "asset_type": "stock",
        "ticker": "DANGCEM",
        "quantity": 100,
        "purchase_price": 300.0,
        "current_price": 350.0,
        "currency_code": "NGN",
        "exchange": "NSE",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Dangote Cement"
    assert data["value_usd"] is not None


def test_portfolio_total_value(client, auth_headers):
    pid = client.post("/api/portfolio/", headers=auth_headers, json={"name": "Total Test"}).get_json()["id"]
    client.post(f"/api/portfolio/{pid}/assets", headers=auth_headers, json={
        "name": "Asset A",
        "asset_type": "cash",
        "quantity": 1,
        "current_price": 1000.0,
        "currency_code": "USD",
    })
    resp = client.get(f"/api/portfolio/{pid}", headers=auth_headers)
    assert resp.get_json()["total_value_usd"] > 0


def test_update_asset(client, auth_headers):
    pid = client.post("/api/portfolio/", headers=auth_headers, json={"name": "P2"}).get_json()["id"]
    asset_resp = client.post(f"/api/portfolio/{pid}/assets", headers=auth_headers, json={
        "name": "MTN Ghana",
        "asset_type": "stock",
        "quantity": 50,
        "current_price": 1.5,
        "currency_code": "GHS",
    })
    aid = asset_resp.get_json()["id"]
    resp = client.put(f"/api/portfolio/{pid}/assets/{aid}", headers=auth_headers, json={"current_price": 2.0})
    assert resp.status_code == 200
    assert resp.get_json()["current_price"] == 2.0


def test_delete_asset(client, auth_headers):
    pid = client.post("/api/portfolio/", headers=auth_headers, json={"name": "P3"}).get_json()["id"]
    aid = client.post(f"/api/portfolio/{pid}/assets", headers=auth_headers, json={
        "name": "Safaricom",
        "asset_type": "stock",
        "quantity": 200,
        "current_price": 25.0,
        "currency_code": "KES",
    }).get_json()["id"]
    resp = client.delete(f"/api/portfolio/{pid}/assets/{aid}", headers=auth_headers)
    assert resp.status_code == 200
