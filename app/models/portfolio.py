from datetime import datetime, timezone
from app import db


class Portfolio(db.Model):
    __tablename__ = "portfolios"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    assets = db.relationship("Asset", backref="portfolio", lazy=True, cascade="all, delete-orphan")

    def total_value_usd(self):
        return sum(a.value_usd or 0 for a in self.assets)

    def to_dict(self, include_assets=False):
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "total_value_usd": self.total_value_usd(),
            "asset_count": len(self.assets),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        if include_assets:
            data["assets"] = [a.to_dict() for a in self.assets]
        return data


class Asset(db.Model):
    __tablename__ = "assets"

    TYPES = ("stock", "bond", "crypto", "real_estate", "commodity", "cash", "other")

    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey("portfolios.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    asset_type = db.Column(db.String(50), nullable=False)
    ticker = db.Column(db.String(20))
    quantity = db.Column(db.Float, default=1.0)
    purchase_price = db.Column(db.Float)
    current_price = db.Column(db.Float)
    currency_code = db.Column(db.String(10), nullable=False)
    value_usd = db.Column(db.Float)
    exchange = db.Column(db.String(100))  # e.g. NSE, JSE, GSE
    acquired_at = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "portfolio_id": self.portfolio_id,
            "name": self.name,
            "asset_type": self.asset_type,
            "ticker": self.ticker,
            "quantity": self.quantity,
            "purchase_price": self.purchase_price,
            "current_price": self.current_price,
            "currency_code": self.currency_code,
            "value_usd": self.value_usd,
            "exchange": self.exchange,
            "acquired_at": self.acquired_at.isoformat() if self.acquired_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
