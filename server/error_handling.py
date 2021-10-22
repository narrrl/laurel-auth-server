import traceback

from authlib.integrations.base_client import MismatchingStateError
from flask import session
from telegram import Bot
from werkzeug.exceptions import NotFound
from werkzeug.utils import redirect

from server.env import Env
from server.user import UnauthorizedError


def error_handling(app):
    @app.errorhandler(NotFound)
    def not_found(_):
        return "route does not exist", 404

    @app.errorhandler(MismatchingStateError)
    def state_error(_):
        # this happens when a user tries authorizing a client with another account
        # as currently is logged in
        return redirect("/auth/logout")

    @app.errorhandler(UnauthorizedError)
    def unauthorized(_):
        return redirect("/auth/login")

    if Env.get_bool("TELEGRAM_LOGGING", required=False):
        bot = Bot(Env.get("TELEGRAM_TOKEN"))

        @app.errorhandler(Exception)
        def all_exception_handler(error):
            bot.sendMessage(chat_id=Env.get("TELEGRAM_CHAT_ID"), text=f"""
            ERROR occurred on AUTH SERVER

            Logged in user: {session.get("user")}

            Error: {type(error).__name__}
            Message: {error}

            Stacktrace:
            {''.join(traceback.format_tb(error.__traceback__))}
            """)
            raise error
