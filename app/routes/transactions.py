from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.transaction import Transaction
from app.models.currency import Currency

transactions_bp = Blueprint("transactions", __name__)


def _compute_usd(amount, currency_code):
    c = Currency.query.filter_by(code=currency_code.upper()).first()
    if c:
        return round(amount / c.usd_rate, 4)
    return None


@transactions_bp.route("/", methods=["GET"])
@jwt_required()
def list_transactions():
    user_id = int(get_jwt_identity())
    query = Transaction.query.filter_by(user_id=user_id)

    # Optional filters
    tx_type = request.args.get("type")
    category = request.args.get("category")
    currency = request.args.get("currency")
    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")

    if tx_type:
        query = query.filter(Transaction.type == tx_type)
    if category:
        query = query.filter(Transaction.category.ilike(f"%{category}%"))
    if currency:
        query = query.filter(Transaction.currency_code == currency.upper())
    if from_date:
        try:
            query = query.filter(Transaction.date >= date.fromisoformat(from_date))
        except ValueError:
            return jsonify({"error": "Invalid from_date format, use YYYY-MM-DD"}), 400
    if to_date:
        try:
            query = query.filter(Transaction.date <= date.fromisoformat(to_date))
        except ValueError:
            return jsonify({"error": "Invalid to_date format, use YYYY-MM-DD"}), 400

    transactions = query.order_by(Transaction.date.desc()).all()
    return jsonify([t.to_dict() for t in transactions]), 200


@transactions_bp.route("/", methods=["POST"])
@jwt_required()
def create_transaction():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    required = ("type", "amount", "currency_code", "date")
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if data["type"] not in Transaction.TYPES:
        return jsonify({"error": f"type must be one of: {', '.join(Transaction.TYPES)}"}), 400

    try:
        amount = float(data["amount"])
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid amount"}), 400

    if amount <= 0:
        return jsonify({"error": "amount must be greater than zero"}), 400

    try:
        tx_date = date.fromisoformat(data["date"])
    except ValueError:
        return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

    tx = Transaction(
        user_id=user_id,
        type=data["type"],
        amount=amount,
        currency_code=data["currency_code"].upper(),
        amount_usd=_compute_usd(amount, data["currency_code"]),
        category=data.get("category"),
        description=data.get("description"),
        date=tx_date,
        reference=data.get("reference"),
    )
    db.session.add(tx)
    db.session.commit()
    return jsonify(tx.to_dict()), 201


@transactions_bp.route("/<int:tx_id>", methods=["GET"])
@jwt_required()
def get_transaction(tx_id):
    user_id = int(get_jwt_identity())
    tx = Transaction.query.filter_by(id=tx_id, user_id=user_id).first()
    if not tx:
        return jsonify({"error": "Transaction not found"}), 404
    return jsonify(tx.to_dict()), 200


@transactions_bp.route("/<int:tx_id>", methods=["PUT"])
@jwt_required()
def update_transaction(tx_id):
    user_id = int(get_jwt_identity())
    tx = Transaction.query.filter_by(id=tx_id, user_id=user_id).first()
    if not tx:
        return jsonify({"error": "Transaction not found"}), 404

    data = request.get_json() or {}
    if "type" in data:
        if data["type"] not in Transaction.TYPES:
            return jsonify({"error": f"type must be one of: {', '.join(Transaction.TYPES)}"}), 400
        tx.type = data["type"]
    if "amount" in data:
        try:
            tx.amount = float(data["amount"])
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid amount"}), 400
    if "currency_code" in data:
        tx.currency_code = data["currency_code"].upper()
    if "category" in data:
        tx.category = data["category"]
    if "description" in data:
        tx.description = data["description"]
    if "date" in data:
        try:
            tx.date = date.fromisoformat(data["date"])
        except ValueError:
            return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400
    if "reference" in data:
        tx.reference = data["reference"]

    tx.amount_usd = _compute_usd(tx.amount, tx.currency_code)
    db.session.commit()
    return jsonify(tx.to_dict()), 200


@transactions_bp.route("/<int:tx_id>", methods=["DELETE"])
@jwt_required()
def delete_transaction(tx_id):
    user_id = int(get_jwt_identity())
    tx = Transaction.query.filter_by(id=tx_id, user_id=user_id).first()
    if not tx:
        return jsonify({"error": "Transaction not found"}), 404
    db.session.delete(tx)
    db.session.commit()
    return jsonify({"message": "Transaction deleted"}), 200
