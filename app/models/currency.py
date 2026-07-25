from app import db


class Currency(db.Model):
    __tablename__ = "currencies"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100))
    symbol = db.Column(db.String(10))
    usd_rate = db.Column(db.Float, nullable=False)  # Units of currency per 1 USD

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "country": self.country,
            "symbol": self.symbol,
            "usd_rate": self.usd_rate,
        }

    @classmethod
    def convert(cls, amount, from_code, to_code):
        """Convert amount from one currency to another via USD."""
        if from_code == to_code:
            return amount
        from_currency = cls.query.filter_by(code=from_code.upper()).first()
        to_currency = cls.query.filter_by(code=to_code.upper()).first()
        if not from_currency or not to_currency:
            return None
        usd_amount = amount / from_currency.usd_rate
        return usd_amount * to_currency.usd_rate
