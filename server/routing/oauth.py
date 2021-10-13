import urllib.parse

from authlib.oauth2 import OAuth2Error
from flask import Blueprint, jsonify, request, redirect

from server.env import Env
from server.user import User
from server.oauth import authorization

oauth = Blueprint("oauth", __name__)


@oauth.route('/authorize', methods=['GET', 'POST'])
def authorize():
    user = User.session_or_none()

    try:
        authorization.validate_consent_request(end_user=user)
    except OAuth2Error as error:
        return jsonify(dict(error.get_body())), 500

    if user:
        return authorization.create_authorization_response(grant_user=user)

    return redirect(f"/auth/login?redirect={urllib.parse.quote(request.url.replace(Env.get('PUBLIC_URL'), ''))}")


@oauth.route('/token', methods=['POST', 'GET'])
def issue_token():
    return authorization.create_token_response()


@oauth.route('/revoke', methods=['POST'])
def revoke_token():
    return authorization.create_endpoint_response('revocation')
