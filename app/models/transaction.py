from datetime import datetime, timezone
from app import db


class Transaction(db.Model):
    __tablename__ = "transactions"

    TYPES = ("income", "expense", "transfer")

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # income | expense | transfer
    amount = db.Column(db.Float, nullable=False)
    currency_code = db.Column(db.String(10), nullable=False)
    amount_usd = db.Column(db.Float)  # auto-computed in USD for analytics
    category = db.Column(db.String(100))
    description = db.Column(db.String(255))
    date = db.Column(db.Date, nullable=False)
    reference = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "type": self.type,
            "amount": self.amount,
            "currency_code": self.currency_code,
            "amount_usd": self.amount_usd,
            "category": self.category,
            "description": self.description,
            "date": self.date.isoformat() if self.date else None,
            "reference": self.reference,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
