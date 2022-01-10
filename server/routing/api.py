from flask import Blueprint, jsonify

from server.routing.decorators import admin_route
from server.oauth import OAuth2Client
from server.user import User

api_bp = Blueprint("api", __name__)


@api_bp.route('/clients', methods=["GET"])
@admin_route
def clients():
    return jsonify(
        [{**client.to_dict(), "metadata": client.client_metadata} for client in OAuth2Client.query.many()])


@api_bp.route('/users', methods=["GET"])
@admin_route
def users():
    return jsonify({user.username: user.to_dict() for user in User.query.many()})


@api_bp.route('/admins', methods=["GET"])
@admin_route
def admins():
    return jsonify({user.username: user.to_dict() for user in User.query.many(role="admin")})


@api_bp.route('/user/<username>', methods=["GET", "POST"])
@admin_route
def user(username):
    user = User.query.one(username=username)
    if not user:
        user = User.query.one(matrikelnummer=username)
        if not user:
            return "user not found", 404
    return jsonify(user.to_dict())
