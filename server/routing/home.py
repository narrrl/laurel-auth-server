from flask import Blueprint, render_template

from server.user import User

home_bp = Blueprint("misc", __name__, static_folder="../../static")


@home_bp.route('/')
def homepage():
    return render_template("home.html", user=User.session_or_unauthorized())


@home_bp.route('/favicon.ico')
def favicon():
    return home_bp.send_static_file("favicon.ico")


@home_bp.route('/static/bootstrap.min.css')
def bootstrap():
    return home_bp.send_static_file('bootstrap.min.css')


@home_bp.route('/static/bootstrap.min.css.map')
def bootstrap_map():
    return "not available", 404


@home_bp.route('/static/logo.svg')
def logo():
    return home_bp.send_static_file('logo.svg')
