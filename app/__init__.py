from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()


def create_app(config=None):
    app = Flask(__name__)

    app.config.setdefault("SECRET_KEY", "dev-secret-key-change-in-production")
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///ecofinance.db")
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    app.config.setdefault("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")

    if config:
        app.config.update(config)

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.currencies import currencies_bp
    from app.routes.transactions import transactions_bp
    from app.routes.portfolio import portfolio_bp
    from app.routes.reports import reports_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(currencies_bp, url_prefix="/api/currencies")
    app.register_blueprint(transactions_bp, url_prefix="/api/transactions")
    app.register_blueprint(portfolio_bp, url_prefix="/api/portfolio")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")

    with app.app_context():
        db.create_all()
        _seed_currencies()

    return app


def _seed_currencies():
    from app.models.currency import Currency

    if Currency.query.count() == 0:
        african_currencies = [
            {"code": "NGN", "name": "Nigerian Naira", "country": "Nigeria", "symbol": "₦", "usd_rate": 1550.0},
            {"code": "KES", "name": "Kenyan Shilling", "country": "Kenya", "symbol": "KSh", "usd_rate": 129.5},
            {"code": "GHS", "name": "Ghanaian Cedi", "country": "Ghana", "symbol": "GH₵", "usd_rate": 15.8},
            {"code": "ZAR", "name": "South African Rand", "country": "South Africa", "symbol": "R", "usd_rate": 18.2},
            {"code": "EGP", "name": "Egyptian Pound", "country": "Egypt", "symbol": "E£", "usd_rate": 50.9},
            {"code": "ETB", "name": "Ethiopian Birr", "country": "Ethiopia", "symbol": "Br", "usd_rate": 121.0},
            {"code": "TZS", "name": "Tanzanian Shilling", "country": "Tanzania", "symbol": "TSh", "usd_rate": 2648.0},
            {"code": "UGX", "name": "Ugandan Shilling", "country": "Uganda", "symbol": "USh", "usd_rate": 3680.0},
            {"code": "XOF", "name": "West African CFA Franc", "country": "West Africa", "symbol": "CFA", "usd_rate": 605.0},
            {"code": "XAF", "name": "Central African CFA Franc", "country": "Central Africa", "symbol": "FCFA", "usd_rate": 605.0},
            {"code": "MAD", "name": "Moroccan Dirham", "country": "Morocco", "symbol": "MAD", "usd_rate": 9.9},
            {"code": "DZD", "name": "Algerian Dinar", "country": "Algeria", "symbol": "DA", "usd_rate": 134.0},
            {"code": "TND", "name": "Tunisian Dinar", "country": "Tunisia", "symbol": "DT", "usd_rate": 3.1},
            {"code": "MZN", "name": "Mozambican Metical", "country": "Mozambique", "symbol": "MT", "usd_rate": 63.5},
            {"code": "RWF", "name": "Rwandan Franc", "country": "Rwanda", "symbol": "RF", "usd_rate": 1350.0},
            {"code": "USD", "name": "US Dollar", "country": "United States", "symbol": "$", "usd_rate": 1.0},
        ]
        for c in african_currencies:
            db.session.add(Currency(**c))
        db.session.commit()
