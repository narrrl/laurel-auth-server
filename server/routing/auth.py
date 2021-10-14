from flask import Blueprint, request, render_template, session, redirect, jsonify

from server.database import database
from server.ldap import get_ldap_user
from server.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/me")
def me():
    user = User.session_or_none()
    if not user:
        return "unauthorized", 401
    return jsonify(user.to_dict()), 200


@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    user = User.session_or_none()
    silent = "silent" in request.args

    def _success():
        if silent:
            return "", 200
        elif "redirect" in request.args:
            return redirect(request.args['redirect'])
        else:
            return redirect("/")

    if request.method == "GET":
        # user already logged in
        if user is not None:
            return _success()

        return render_template("login.html")

    # session is valid already
    if user is not None:
        return ("", 200) if silent else redirect("/")

    def _error(msg):
        return (msg, 401) if silent else render_template("login.html", message=msg)

    # check if login attempt is via json data
    data = request.get_json(silent=True)

    # check if user logged in via form data
    if not data:
        data = request.form


    if "username" not in data or "password" not in data:
        return _error("Missing credentials")

    username = data["username"].strip()
    password = data["password"].strip()

    user = User.query.one(username=username)

    # get user object from ldap
    # this includes checking the credentials
    ldap_user, error = get_ldap_user(username, password)

    if error is not None:
        return _error(error)

    # add user to database if not exist or update if necessary
    if user is None:
        with database as db:
            db += ldap_user
        user = ldap_user
    elif user != ldap_user:
        user.update(ldap_user)

    session['id'] = user.id
    session.permanent = True

    return _success()


@auth_bp.route('/logout')
def logout():
    if User.session_or_none():
        del session['id']

    if "redirect" in request.args.keys():
        return redirect(request.args['redirect'])

    return redirect('/auth/login')
