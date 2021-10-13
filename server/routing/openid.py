from authlib.integrations.flask_oauth2 import current_token
from authlib.jose import JsonWebKey
from flask import Blueprint, jsonify

from server.env import Env
from server.oauth import require_oauth, generate_user_info

openid_bp = Blueprint("openid", __name__)


@openid_bp.route('/userinfo')
@require_oauth('profile')
def userinfo():
    return jsonify(generate_user_info(current_token.user, current_token.scope))


@openid_bp.route("/.well-known/openid-configuration", methods=["GET"])
def discovery():
    return jsonify(Env.get_openid_config())


@openid_bp.route("/.well-known/jwks", methods=['GET'])
def jwks():
    return {"keys": [{**JsonWebKey.import_key(Env.get("PUBLIC_KEY")), "kty": "RSA"}]}
