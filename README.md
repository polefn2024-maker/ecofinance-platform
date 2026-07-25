# ecofinance-platform

**African Financial Intelligence Platform**

A RESTful API platform that empowers individuals and organisations across Africa to track transactions, manage investment portfolios, and generate financial intelligence reports — all with first-class support for African currencies.

---

## Features

| Feature | Description |
|---|---|
| **Authentication** | JWT-based registration and login |
| **African Currencies** | 16 African currencies pre-seeded with USD exchange rates |
| **Currency Conversion** | Convert between any two supported currencies |
| **Transaction Management** | Full CRUD for income, expense, and transfer transactions |
| **Portfolio & Assets** | Manage investment portfolios and track individual assets (stocks, bonds, crypto, etc.) |
| **Financial Reports** | Summary, by-category, by-currency, and monthly breakdown reports |

---

## Tech Stack

- **Python 3.12** with **Flask 3**
- **SQLAlchemy** (ORM) with SQLite (default; swap for PostgreSQL in production)
- **Flask-JWT-Extended** for authentication
- **Flask-Bcrypt** for password hashing
- **pytest** for testing

---

## Supported African Currencies

| Code | Currency | Country |
|---|---|---|
| NGN | Nigerian Naira | Nigeria |
| KES | Kenyan Shilling | Kenya |
| GHS | Ghanaian Cedi | Ghana |
| ZAR | South African Rand | South Africa |
| EGP | Egyptian Pound | Egypt |
| ETB | Ethiopian Birr | Ethiopia |
| TZS | Tanzanian Shilling | Tanzania |
| UGX | Ugandan Shilling | Uganda |
| XOF | West African CFA Franc | West Africa |
| XAF | Central African CFA Franc | Central Africa |
| MAD | Moroccan Dirham | Morocco |
| DZD | Algerian Dinar | Algeria |
| TND | Tunisian Dinar | Tunisia |
| MZN | Mozambican Metical | Mozambique |
| RWF | Rwandan Franc | Rwanda |
| USD | US Dollar | United States |

---

## Setup

```bash
# 1. Clone and enter the project
git clone https://github.com/polefn2024-maker/ecofinance-platform.git
cd ecofinance-platform

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the development server
python run.py
```

The API is available at `http://localhost:5000`.

---

## Running Tests

```bash
pytest tests/ -v
```

---

## API Reference

All authenticated endpoints require:
```
Authorization: Bearer <your_access_token>
```

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Register a new user |
| POST | `/api/auth/login` | Login and receive a JWT |
| GET | `/api/auth/profile` | Get the current user's profile |
| PUT | `/api/auth/profile` | Update the current user's profile |

**Register body:**
```json
{
  "username": "adaeze",
  "email": "adaeze@example.com",
  "password": "SecurePass123",
  "full_name": "Adaeze Okafor",
  "country": "Nigeria",
  "base_currency": "NGN"
}
```

### Currencies

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/currencies/` | No | List all currencies |
| GET | `/api/currencies/<code>` | No | Get a currency by code |
| GET | `/api/currencies/convert?from=NGN&to=USD&amount=5000` | Yes | Convert between currencies |
| PUT | `/api/currencies/<code>/rate` | Yes | Update a currency's USD rate |

### Transactions

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/transactions/` | Yes | List transactions (supports filters) |
| POST | `/api/transactions/` | Yes | Create a transaction |
| GET | `/api/transactions/<id>` | Yes | Get a transaction |
| PUT | `/api/transactions/<id>` | Yes | Update a transaction |
| DELETE | `/api/transactions/<id>` | Yes | Delete a transaction |

**Filters:** `?type=income|expense|transfer`, `?category=<name>`, `?currency=NGN`, `?from_date=2024-01-01`, `?to_date=2024-12-31`

**Transaction body:**
```json
{
  "type": "income",
  "amount": 150000,
  "currency_code": "NGN",
  "date": "2024-03-15",
  "category": "Salary",
  "description": "March salary payment",
  "reference": "REF-001"
}
```

### Portfolio

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/portfolio/` | Yes | List portfolios |
| POST | `/api/portfolio/` | Yes | Create a portfolio |
| GET | `/api/portfolio/<id>` | Yes | Get a portfolio with assets |
| PUT | `/api/portfolio/<id>` | Yes | Update a portfolio |
| DELETE | `/api/portfolio/<id>` | Yes | Delete a portfolio |
| POST | `/api/portfolio/<id>/assets` | Yes | Add an asset |
| PUT | `/api/portfolio/<id>/assets/<aid>` | Yes | Update an asset |
| DELETE | `/api/portfolio/<id>/assets/<aid>` | Yes | Delete an asset |

**Asset types:** `stock`, `bond`, `crypto`, `real_estate`, `commodity`, `cash`, `other`

### Reports

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/reports/summary` | Yes | Overall income/expense summary |
| GET | `/api/reports/by-category` | Yes | Breakdown by transaction category |
| GET | `/api/reports/by-currency` | Yes | Breakdown by currency |
| GET | `/api/reports/monthly` | Yes | Monthly income and expense totals |

All report endpoints support optional `?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD` filters.

---

## Production Notes

- Replace `SECRET_KEY` and `JWT_SECRET_KEY` with secure random values via environment variables.
- Swap `SQLALCHEMY_DATABASE_URI` for a production-grade database (e.g. PostgreSQL).
- Run behind a production WSGI server such as Gunicorn.
