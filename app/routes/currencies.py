from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.models.currency import Currency

currencies_bp = Blueprint("currencies", __name__)


@currencies_bp.route("/", methods=["GET"])
def list_currencies():
    currencies = Currency.query.order_by(Currency.code).all()
    return jsonify([c.to_dict() for c in currencies]), 200


@currencies_bp.route("/<string:code>", methods=["GET"])
def get_currency(code):
    currency = Currency.query.filter_by(code=code.upper()).first()
    if not currency:
        return jsonify({"error": f"Currency '{code}' not found"}), 404
    return jsonify(currency.to_dict()), 200


@currencies_bp.route("/convert", methods=["GET"])
@jwt_required()
def convert():
    from_code = request.args.get("from", "").upper()
    to_code = request.args.get("to", "").upper()
    try:
        amount = float(request.args.get("amount", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid amount"}), 400

    if not from_code or not to_code:
        return jsonify({"error": "Query params 'from' and 'to' are required"}), 400
    if amount <= 0:
        return jsonify({"error": "Amount must be greater than 0"}), 400

    result = Currency.convert(amount, from_code, to_code)
    if result is None:
        return jsonify({"error": "One or both currency codes not found"}), 404

    return jsonify({
        "from": from_code,
        "to": to_code,
        "amount": amount,
        "converted": round(result, 4),
    }), 200


@currencies_bp.route("/<string:code>/rate", methods=["PUT"])
@jwt_required()
def update_rate(code):
    """Update the USD exchange rate for a currency."""
    currency = Currency.query.filter_by(code=code.upper()).first()
    if not currency:
        return jsonify({"error": f"Currency '{code}' not found"}), 404

    data = request.get_json() or {}
    try:
        rate = float(data.get("usd_rate", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid usd_rate"}), 400

    if rate <= 0:
        return jsonify({"error": "usd_rate must be greater than 0"}), 400

    from app import db
    currency.usd_rate = rate
    db.session.commit()
    return jsonify(currency.to_dict()), 200
