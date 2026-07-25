from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.portfolio import Portfolio, Asset
from app.models.currency import Currency

portfolio_bp = Blueprint("portfolio", __name__)


def _compute_value_usd(quantity, current_price, currency_code):
    if current_price is None or quantity is None:
        return None
    c = Currency.query.filter_by(code=currency_code.upper()).first()
    if c:
        return round((quantity * current_price) / c.usd_rate, 4)
    return None


@portfolio_bp.route("/", methods=["GET"])
@jwt_required()
def list_portfolios():
    user_id = int(get_jwt_identity())
    portfolios = Portfolio.query.filter_by(user_id=user_id).all()
    return jsonify([p.to_dict() for p in portfolios]), 200


@portfolio_bp.route("/", methods=["POST"])
@jwt_required()
def create_portfolio():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Portfolio name is required"}), 400

    portfolio = Portfolio(
        user_id=user_id,
        name=data["name"],
        description=data.get("description"),
    )
    db.session.add(portfolio)
    db.session.commit()
    return jsonify(portfolio.to_dict()), 201


@portfolio_bp.route("/<int:portfolio_id>", methods=["GET"])
@jwt_required()
def get_portfolio(portfolio_id):
    user_id = int(get_jwt_identity())
    portfolio = Portfolio.query.filter_by(id=portfolio_id, user_id=user_id).first()
    if not portfolio:
        return jsonify({"error": "Portfolio not found"}), 404
    return jsonify(portfolio.to_dict(include_assets=True)), 200


@portfolio_bp.route("/<int:portfolio_id>", methods=["PUT"])
@jwt_required()
def update_portfolio(portfolio_id):
    user_id = int(get_jwt_identity())
    portfolio = Portfolio.query.filter_by(id=portfolio_id, user_id=user_id).first()
    if not portfolio:
        return jsonify({"error": "Portfolio not found"}), 404

    data = request.get_json() or {}
    if "name" in data:
        portfolio.name = data["name"]
    if "description" in data:
        portfolio.description = data["description"]

    db.session.commit()
    return jsonify(portfolio.to_dict()), 200


@portfolio_bp.route("/<int:portfolio_id>", methods=["DELETE"])
@jwt_required()
def delete_portfolio(portfolio_id):
    user_id = int(get_jwt_identity())
    portfolio = Portfolio.query.filter_by(id=portfolio_id, user_id=user_id).first()
    if not portfolio:
        return jsonify({"error": "Portfolio not found"}), 404
    db.session.delete(portfolio)
    db.session.commit()
    return jsonify({"message": "Portfolio deleted"}), 200


# ── Assets ──────────────────────────────────────────────────────────────────

@portfolio_bp.route("/<int:portfolio_id>/assets", methods=["POST"])
@jwt_required()
def add_asset(portfolio_id):
    user_id = int(get_jwt_identity())
    portfolio = Portfolio.query.filter_by(id=portfolio_id, user_id=user_id).first()
    if not portfolio:
        return jsonify({"error": "Portfolio not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    required = ("name", "asset_type", "currency_code")
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if data["asset_type"] not in Asset.TYPES:
        return jsonify({"error": f"asset_type must be one of: {', '.join(Asset.TYPES)}"}), 400

    try:
        quantity = float(data.get("quantity", 1.0))
        purchase_price = float(data["purchase_price"]) if data.get("purchase_price") is not None else None
        current_price = float(data["current_price"]) if data.get("current_price") is not None else None
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid numeric value"}), 400

    acquired_at = None
    if data.get("acquired_at"):
        try:
            acquired_at = date.fromisoformat(data["acquired_at"])
        except ValueError:
            return jsonify({"error": "Invalid acquired_at format, use YYYY-MM-DD"}), 400

    asset = Asset(
        portfolio_id=portfolio_id,
        name=data["name"],
        asset_type=data["asset_type"],
        ticker=data.get("ticker"),
        quantity=quantity,
        purchase_price=purchase_price,
        current_price=current_price,
        currency_code=data["currency_code"].upper(),
        value_usd=_compute_value_usd(quantity, current_price, data["currency_code"]),
        exchange=data.get("exchange"),
        acquired_at=acquired_at,
    )
    db.session.add(asset)
    db.session.commit()
    return jsonify(asset.to_dict()), 201


@portfolio_bp.route("/<int:portfolio_id>/assets/<int:asset_id>", methods=["PUT"])
@jwt_required()
def update_asset(portfolio_id, asset_id):
    user_id = int(get_jwt_identity())
    portfolio = Portfolio.query.filter_by(id=portfolio_id, user_id=user_id).first()
    if not portfolio:
        return jsonify({"error": "Portfolio not found"}), 404

    asset = Asset.query.filter_by(id=asset_id, portfolio_id=portfolio_id).first()
    if not asset:
        return jsonify({"error": "Asset not found"}), 404

    data = request.get_json() or {}
    updatable = ("name", "ticker", "exchange")
    for field in updatable:
        if field in data:
            setattr(asset, field, data[field])

    if "asset_type" in data:
        if data["asset_type"] not in Asset.TYPES:
            return jsonify({"error": f"asset_type must be one of: {', '.join(Asset.TYPES)}"}), 400
        asset.asset_type = data["asset_type"]
    if "quantity" in data:
        try:
            asset.quantity = float(data["quantity"])
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid quantity"}), 400
    if "current_price" in data:
        try:
            asset.current_price = float(data["current_price"])
        except (TypeError, ValueError):
            return jsonify({"error": "Invalid current_price"}), 400
    if "currency_code" in data:
        asset.currency_code = data["currency_code"].upper()

    asset.value_usd = _compute_value_usd(asset.quantity, asset.current_price, asset.currency_code)
    db.session.commit()
    return jsonify(asset.to_dict()), 200


@portfolio_bp.route("/<int:portfolio_id>/assets/<int:asset_id>", methods=["DELETE"])
@jwt_required()
def delete_asset(portfolio_id, asset_id):
    user_id = int(get_jwt_identity())
    portfolio = Portfolio.query.filter_by(id=portfolio_id, user_id=user_id).first()
    if not portfolio:
        return jsonify({"error": "Portfolio not found"}), 404

    asset = Asset.query.filter_by(id=asset_id, portfolio_id=portfolio_id).first()
    if not asset:
        return jsonify({"error": "Asset not found"}), 404

    db.session.delete(asset)
    db.session.commit()
    return jsonify({"message": "Asset deleted"}), 200
