from sqlalchemy import UniqueConstraint, Integer, Column, ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import gen_salt

from server.env import Env
from server.database import database
from server.user import User
from authlib.integrations.flask_oauth2 import (
    AuthorizationServer,
    ResourceProtector,
)
from authlib.integrations.sqla_oauth2 import (
    create_query_client_func,
    create_save_token_func,
    create_bearer_token_validator, OAuth2ClientMixin, OAuth2AuthorizationCodeMixin, OAuth2TokenMixin,
)
from authlib.oauth2.rfc6749.grants import (
    AuthorizationCodeGrant as _AuthorizationCodeGrant,
)
from authlib.oidc.core import UserInfo
from authlib.oidc.core.grants import (
    OpenIDCode as _OpenIDCode,
    OpenIDImplicitGrant as _OpenIDImplicitGrant,
    OpenIDHybridGrant as _OpenIDHybridGrant,
)

authorization = AuthorizationServer()
require_oauth = ResourceProtector()


def config_oauth(app):
    query_client = create_query_client_func(database.session, OAuth2Client)
    save_token = create_save_token_func(database.session, OAuth2Token)
    authorization.init_app(
        app,
        query_client=query_client,
        save_token=save_token
    )

    # support all openid grants
    authorization.register_grant(AuthorizationCodeGrant, [
        OpenIDCode(),
    ])
    authorization.register_grant(ImplicitGrant)
    authorization.register_grant(HybridGrant)

    # protect resource
    bearer_cls = create_bearer_token_validator(database.session, OAuth2Token)
    require_oauth.register_token_validator(bearer_cls())


def get_jwt_config():
    return {
        "key": Env.get("PRIVATE_KEY"),
        "alg": "RS256",
        "iss": Env.get("PUBLIC_URL"),
        "exp": 3600
    }


def generate_user_info(user, scope):
    info = {
        'sub': user.username,
    }

    if 'email' in scope:
        info['email'] = user.email

    if 'profile' in scope:
        info['matrikelnummer'] = user.matrikelnummer
        info['name'] = user.name
        info['role'] = user.role

    return UserInfo(**info)


def create_authorization_code(client, grant_user, request):
    code = gen_salt(32)
    nonce = request.data.get('nonce')
    with database as db:
        db += OAuth2AuthorizationCode(
            code=code,
            client_id=client.client_id,
            redirect_uri=request.redirect_uri,
            scope=request.scope,
            user_id=grant_user.id,
            nonce=nonce,
        )
    return code


def exists_nonce(nonce, req):
    return OAuth2AuthorizationCode.query.exists(client_id=req.client_id, nonce=nonce)


class OAuth2Client(database.Model, OAuth2ClientMixin):
    __tablename__ = 'oauth2_client'

    __table_args__ = (UniqueConstraint('client_id', name='_client_uc'),)

    id = Column(Integer, primary_key=True)


class OAuth2AuthorizationCode(database.Model, OAuth2AuthorizationCodeMixin):
    __tablename__ = 'oauth2_code'

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship('User')


class OAuth2Token(database.Model, OAuth2TokenMixin):
    __tablename__ = 'oauth2_token'

    id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey('user.id', ondelete='CASCADE'))
    user = relationship('User')


class AuthorizationCodeGrant(_AuthorizationCodeGrant):
    def save_authorization_code(self, code, request):
        pass

    def create_authorization_code(self, client, grant_user, request):
        return create_authorization_code(client, grant_user, request)

    def parse_authorization_code(self, code, client):
        item = OAuth2AuthorizationCode.query.filter_by(
            code=code,
            client_id=client.client_id,
        ).first()
        if item and not item.is_expired():
            return item

    def delete_authorization_code(self, authorization_code):
        with database as db:
            db -= authorization_code

    def authenticate_user(self, authorization_code):
        return User.query.get(authorization_code.user_id)


class OpenIDCode(_OpenIDCode):
    def exists_nonce(self, nonce, request):
        return exists_nonce(nonce, request)

    def get_jwt_config(self, grant):
        return get_jwt_config()

    def generate_user_info(self, user, scope):
        return generate_user_info(user, scope)


class ImplicitGrant(_OpenIDImplicitGrant):
    def exists_nonce(self, nonce, request):
        return exists_nonce(nonce, request)

    def get_jwt_config(self):
        return get_jwt_config()

    def generate_user_info(self, user, scope):
        return generate_user_info(user, scope)


class HybridGrant(_OpenIDHybridGrant):
    def save_authorization_code(self, code, request):
        pass

    def create_authorization_code(self, client, grant_user, request):
        return create_authorization_code(client, grant_user, request)

    def exists_nonce(self, nonce, request):
        return exists_nonce(nonce, request)

    def get_jwt_config(self):
        return get_jwt_config()

    def generate_user_info(self, user, scope):
        return generate_user_info(user, scope)
