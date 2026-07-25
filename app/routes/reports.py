from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from app.models.transaction import Transaction

reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/summary", methods=["GET"])
@jwt_required()
def summary():
    """Return overall income/expense summary for the authenticated user."""
    user_id = int(get_jwt_identity())

    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")

    from datetime import date as date_type

    query = Transaction.query.filter_by(user_id=user_id)
    if from_date:
        try:
            query = query.filter(Transaction.date >= date_type.fromisoformat(from_date))
        except ValueError:
            return jsonify({"error": "Invalid from_date"}), 400
    if to_date:
        try:
            query = query.filter(Transaction.date <= date_type.fromisoformat(to_date))
        except ValueError:
            return jsonify({"error": "Invalid to_date"}), 400

    transactions = query.all()

    total_income_usd = sum(t.amount_usd or 0 for t in transactions if t.type == "income")
    total_expense_usd = sum(t.amount_usd or 0 for t in transactions if t.type == "expense")
    net_usd = total_income_usd - total_expense_usd

    return jsonify({
        "total_income_usd": round(total_income_usd, 4),
        "total_expense_usd": round(total_expense_usd, 4),
        "net_usd": round(net_usd, 4),
        "transaction_count": len(transactions),
    }), 200


@reports_bp.route("/by-category", methods=["GET"])
@jwt_required()
def by_category():
    """Breakdown of transactions by category."""
    user_id = int(get_jwt_identity())

    from datetime import date as date_type

    from_date = request.args.get("from_date")
    to_date = request.args.get("to_date")

    query = Transaction.query.filter_by(user_id=user_id)
    if from_date:
        try:
            query = query.filter(Transaction.date >= date_type.fromisoformat(from_date))
        except ValueError:
            return jsonify({"error": "Invalid from_date"}), 400
    if to_date:
        try:
            query = query.filter(Transaction.date <= date_type.fromisoformat(to_date))
        except ValueError:
            return jsonify({"error": "Invalid to_date"}), 400

    transactions = query.all()

    breakdown = {}
    for t in transactions:
        cat = t.category or "Uncategorized"
        if cat not in breakdown:
            breakdown[cat] = {"income_usd": 0.0, "expense_usd": 0.0, "count": 0}
        if t.type == "income":
            breakdown[cat]["income_usd"] += t.amount_usd or 0
        elif t.type == "expense":
            breakdown[cat]["expense_usd"] += t.amount_usd or 0
        breakdown[cat]["count"] += 1

    result = [
        {
            "category": cat,
            "income_usd": round(v["income_usd"], 4),
            "expense_usd": round(v["expense_usd"], 4),
            "count": v["count"],
        }
        for cat, v in sorted(breakdown.items())
    ]
    return jsonify(result), 200


@reports_bp.route("/by-currency", methods=["GET"])
@jwt_required()
def by_currency():
    """Breakdown of transactions by currency."""
    user_id = int(get_jwt_identity())

    transactions = Transaction.query.filter_by(user_id=user_id).all()

    breakdown = {}
    for t in transactions:
        code = t.currency_code
        if code not in breakdown:
            breakdown[code] = {"total_amount": 0.0, "total_usd": 0.0, "count": 0}
        breakdown[code]["total_amount"] += t.amount
        breakdown[code]["total_usd"] += t.amount_usd or 0
        breakdown[code]["count"] += 1

    result = [
        {
            "currency_code": code,
            "total_amount": round(v["total_amount"], 4),
            "total_usd": round(v["total_usd"], 4),
            "count": v["count"],
        }
        for code, v in sorted(breakdown.items())
    ]
    return jsonify(result), 200


@reports_bp.route("/monthly", methods=["GET"])
@jwt_required()
def monthly():
    """Monthly income and expense totals."""
    user_id = int(get_jwt_identity())

    transactions = Transaction.query.filter_by(user_id=user_id).all()

    monthly_data = {}
    for t in transactions:
        key = t.date.strftime("%Y-%m") if t.date else "Unknown"
        if key not in monthly_data:
            monthly_data[key] = {"income_usd": 0.0, "expense_usd": 0.0, "count": 0}
        if t.type == "income":
            monthly_data[key]["income_usd"] += t.amount_usd or 0
        elif t.type == "expense":
            monthly_data[key]["expense_usd"] += t.amount_usd or 0
        monthly_data[key]["count"] += 1

    result = [
        {
            "month": month,
            "income_usd": round(v["income_usd"], 4),
            "expense_usd": round(v["expense_usd"], 4),
            "net_usd": round(v["income_usd"] - v["expense_usd"], 4),
            "count": v["count"],
        }
        for month, v in sorted(monthly_data.items())
    ]
    return jsonify(result), 200
