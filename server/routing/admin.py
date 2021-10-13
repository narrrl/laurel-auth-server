import time

from flask import Blueprint, render_template, request, redirect
from werkzeug.security import gen_salt

from server.database import database
from server.routing.decorators import admin_route
from server.oauth import OAuth2Client
from server.user import User

admin_bp = Blueprint("admin", __name__)


@admin_bp.route('/')
@admin_route
def homepage():
    return redirect("/admin/clients")


@admin_bp.route('/clients', methods=["GET", "POST"])
@admin_bp.route('/clients/extend', methods=["GET", "POST"])
@admin_route
def clients():
    return render_template("admin/clients.html", clients=OAuth2Client.query.many())


@admin_bp.route('/users', methods=["GET", "POST"])
@admin_bp.route('/users/extend', methods=["GET", "POST"])
@admin_route
def users():
    return render_template("admin/users.html", users=User.query.many())


@admin_bp.route('/clients/delete/', methods=["POST"])
@admin_route
def delete_client():
    data = request.get_json(silent=True)

    if not data:
        data = request.form

    if not data["id"]:
        return "no id passed to delete", 500

    try:
        id = int(data["id"])
    except ValueError:
        return "invalid id passed to delete", 500

    with database:
        OAuth2Client.query.delete_by(id=id)
    return redirect("/admin/clients")


@admin_bp.route('/users/delete', methods=["POST"])
@admin_route
def delete_user():
    # allow json requests
    data = request.get_json(silent=True)

    if not data:
        data = request.form

    if not data["id"]:
        return "no id passed to delete", 500

    try:
        id = int(data["id"])
    except ValueError:
        return "invalid id passed to delete", 500

    with database:
        User.query.delete_by(id=id)
    return redirect("/admin/users")


@admin_bp.route('/clients/add', methods=["GET", "POST"])
@admin_route
def add_client():
    user = User.session_or_unauthorized(admin=True)
    if request.method == "GET":
        return render_template("admin/add_client.html", user=user)

    def _split_by_crlf(s):
        return [v for v in s.splitlines() if v]

    # allow json requests
    data = request.get_json(silent=True)

    if not data:
        data = request.form

    if "client_name" not in data or "client_uri" not in data:
        return "missing info", 500

    client = OAuth2Client(client_id=gen_salt(24))
    client.client_id_issued_at = int(time.time())  # not set by mixin
    client.client_secret = '' if client.token_endpoint_auth_method == 'none' else gen_salt(48)
    client.set_client_metadata({
        "client_name": data["client_name"],
        "client_uri": data["client_uri"],
        "grant_types": _split_by_crlf(data["grant_type"]),
        "redirect_uris": _split_by_crlf(data["redirect_uri"]),
        "response_types": _split_by_crlf(data["response_type"]),
        "scope": data["scope"],
        "token_endpoint_auth_method": data["token_endpoint_auth_method"],
        "author_name": user.name,
        "author": user.username
    })

    with database as db:
        db += client

    return redirect("/admin/clients")
