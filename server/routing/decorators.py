import functools

from flask import request, Response

from server.env import Env
from server.user import User



def admin_route(f):
    @functools.wraps(f)
    def decorated_function(*args, **kws):
        if request.headers.get("Authorization") != Env.get("ADMIN_KEY"):
            User.session_or_unauthorized(admin=True)
        return f(*args, **kws)

    return decorated_function
