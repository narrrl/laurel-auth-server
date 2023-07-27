from flask import Blueprint, render_template
import segno
from cryptography.fernet import Fernet

from server.env import Env
from server.user import User

home_bp = Blueprint("misc", __name__, static_folder="../../static")


@home_bp.route('/')
def homepage():
    user = User.session_or_unauthorized()
    f = Fernet(Env.get("FERNET_KEY").encode("utf-8"))
    qr = segno.make(f.encrypt(user.username.encode("utf-8")), error='H')
    return render_template("home.html", user=User.session_or_unauthorized(), qr=qr)


@home_bp.route('/favicon.ico')
def favicon():
    return home_bp.send_static_file("favicon.ico")


@home_bp.route('/static/bootstrap.min.css')
def bootstrap():
    return home_bp.send_static_file('bootstrap.min.css')


@home_bp.route('/static/logo.svg')
def logo():
    return home_bp.send_static_file('logo.svg')
