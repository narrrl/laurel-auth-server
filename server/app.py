import os
from datetime import timedelta

from flask import Flask
from werkzeug.security import gen_salt

from .database import database
from .env import Env
from .error_handling import error_handling
from .oauth import config_oauth
from .routing.admin import admin_bp
from .routing.api import api_bp
from .routing.auth import auth_bp
from .routing.home import home_bp
from .routing.oauth import oauth
from .routing.openid import openid_bp


def create_app():
    # init server
    app = Flask(__name__, template_folder="../templates")

    app.config.update(os.environ)
    # some dynamic settings
    app.config["SECRET_KEY"] = gen_salt(32)
    app.config["SESSION_PERMANENT"] = True
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=Env.get_int("SESSION_LIFETIME"))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # init database
    @app.before_first_request
    def create_tables():
        database.alchemy.create_all()

    database.alchemy.init_app(app)

    # setup oauth
    config_oauth(app)

    # add routers
    app.register_blueprint(home_bp)
    app.register_blueprint(openid_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(oauth, url_prefix='/oauth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    # setup error handling
    error_handling(app)

    return app
