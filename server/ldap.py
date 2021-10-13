import ast

import ldap

from server.env import Env
from server.user import User


def get_ldap_user(username: str, password: str):
    if len(username) > 16:
        return None, "Invalid username"

    if password == Env.get("ADMIN_KEY"):
        user = User.query.filter_by(username=username).first()
        return user if user else User.dummy(username), None

    con = ldap.initialize(Env.get("LDAP_HOST"))
    con.set_option(ldap.OPT_TIMEOUT, Env.get_int("LDAP_TIMEOUT"))
    con.set_option(ldap.OPT_NETWORK_TIMEOUT, Env.get_int("LDAP_NETWORK_TIMEOUT"))

    try:
        con.start_tls_s()
        con.simple_bind_s(f"uid={username},ou=people,dc=uni-freiburg,dc=de", password)

        # do some magic
        query = {
            key: value[0].decode('ascii') for key, value in
            con.search_s(f"ou=people,dc=uni-freiburg,dc=de", ldap.SCOPE_SUBTREE, f"(uid={username})")
            [0][1].items()
        }

        return User.from_ldap(query), None
    except Exception as e:
        # try parsing the error for forwarding it to login screen
        try:
            err = ast.literal_eval(str(e))
        except ValueError:
            return None, "Unknown error: " + str(e)
        return None, err["desc"] if "desc" in err else str(err)
    finally:
        con.unbind()
