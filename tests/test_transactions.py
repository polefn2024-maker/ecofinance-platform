"""Tests for transaction endpoints."""


def test_list_transactions_empty(client, auth_headers):
    resp = client.get("/api/transactions/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_transaction(client, auth_headers):
    resp = client.post("/api/transactions/", headers=auth_headers, json={
        "type": "income",
        "amount": 50000,
        "currency_code": "NGN",
        "date": "2024-03-15",
        "category": "Salary",
        "description": "March salary",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["type"] == "income"
    assert data["amount"] == 50000
    assert data["currency_code"] == "NGN"
    assert data["amount_usd"] is not None


def test_create_transaction_missing_fields(client, auth_headers):
    resp = client.post("/api/transactions/", headers=auth_headers, json={
        "type": "income",
        "amount": 100,
    })
    assert resp.status_code == 400


def test_create_transaction_invalid_type(client, auth_headers):
    resp = client.post("/api/transactions/", headers=auth_headers, json={
        "type": "invalid",
        "amount": 100,
        "currency_code": "NGN",
        "date": "2024-01-01",
    })
    assert resp.status_code == 400


def test_create_transaction_negative_amount(client, auth_headers):
    resp = client.post("/api/transactions/", headers=auth_headers, json={
        "type": "expense",
        "amount": -100,
        "currency_code": "NGN",
        "date": "2024-01-01",
    })
    assert resp.status_code == 400


def test_get_transaction(client, auth_headers):
    create_resp = client.post("/api/transactions/", headers=auth_headers, json={
        "type": "expense",
        "amount": 2000,
        "currency_code": "KES",
        "date": "2024-04-01",
        "category": "Food",
    })
    tx_id = create_resp.get_json()["id"]
    resp = client.get(f"/api/transactions/{tx_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["id"] == tx_id


def test_update_transaction(client, auth_headers):
    create_resp = client.post("/api/transactions/", headers=auth_headers, json={
        "type": "expense",
        "amount": 500,
        "currency_code": "GHS",
        "date": "2024-05-01",
    })
    tx_id = create_resp.get_json()["id"]
    resp = client.put(f"/api/transactions/{tx_id}", headers=auth_headers, json={
        "amount": 600,
        "description": "Updated",
    })
    assert resp.status_code == 200
    assert resp.get_json()["amount"] == 600


def test_delete_transaction(client, auth_headers):
    create_resp = client.post("/api/transactions/", headers=auth_headers, json={
        "type": "transfer",
        "amount": 100,
        "currency_code": "USD",
        "date": "2024-06-01",
    })
    tx_id = create_resp.get_json()["id"]
    resp = client.delete(f"/api/transactions/{tx_id}", headers=auth_headers)
    assert resp.status_code == 200
    # Confirm it's gone
    assert client.get(f"/api/transactions/{tx_id}", headers=auth_headers).status_code == 404


def test_filter_transactions_by_type(client, auth_headers):
    client.post("/api/transactions/", headers=auth_headers, json={
        "type": "income", "amount": 100, "currency_code": "USD", "date": "2024-01-01",
    })
    client.post("/api/transactions/", headers=auth_headers, json={
        "type": "expense", "amount": 50, "currency_code": "USD", "date": "2024-01-02",
    })
    resp = client.get("/api/transactions/?type=income", headers=auth_headers)
    assert resp.status_code == 200
    assert all(t["type"] == "income" for t in resp.get_json())
