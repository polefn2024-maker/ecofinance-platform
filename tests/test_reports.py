"""Tests for financial reports endpoints."""


def _add_transactions(client, auth_headers):
    """Helper to seed transactions."""
    client.post("/api/transactions/", headers=auth_headers, json={
        "type": "income", "amount": 100000, "currency_code": "NGN",
        "date": "2024-01-10", "category": "Salary",
    })
    client.post("/api/transactions/", headers=auth_headers, json={
        "type": "expense", "amount": 20000, "currency_code": "NGN",
        "date": "2024-01-15", "category": "Food",
    })
    client.post("/api/transactions/", headers=auth_headers, json={
        "type": "income", "amount": 500, "currency_code": "USD",
        "date": "2024-02-05", "category": "Freelance",
    })
    client.post("/api/transactions/", headers=auth_headers, json={
        "type": "expense", "amount": 200, "currency_code": "USD",
        "date": "2024-02-20", "category": "Utilities",
    })


def test_summary(client, auth_headers):
    _add_transactions(client, auth_headers)
    resp = client.get("/api/reports/summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total_income_usd"] > 0
    assert data["total_expense_usd"] > 0
    assert data["transaction_count"] == 4


def test_summary_date_filter(client, auth_headers):
    _add_transactions(client, auth_headers)
    resp = client.get("/api/reports/summary?from_date=2024-02-01", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["transaction_count"] == 2


def test_by_category(client, auth_headers):
    _add_transactions(client, auth_headers)
    resp = client.get("/api/reports/by-category", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    categories = [row["category"] for row in data]
    assert "Salary" in categories
    assert "Food" in categories


def test_by_currency(client, auth_headers):
    _add_transactions(client, auth_headers)
    resp = client.get("/api/reports/by-currency", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    codes = [row["currency_code"] for row in data]
    assert "NGN" in codes
    assert "USD" in codes


def test_monthly(client, auth_headers):
    _add_transactions(client, auth_headers)
    resp = client.get("/api/reports/monthly", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    months = [row["month"] for row in data]
    assert "2024-01" in months
    assert "2024-02" in months
    for row in data:
        assert "net_usd" in row


def test_reports_require_auth(client):
    assert client.get("/api/reports/summary").status_code == 401
    assert client.get("/api/reports/by-category").status_code == 401
    assert client.get("/api/reports/by-currency").status_code == 401
    assert client.get("/api/reports/monthly").status_code == 401
