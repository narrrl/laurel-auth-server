import os

from Crypto.PublicKey import RSA
from dotenv import load_dotenv


class Env:
    @staticmethod
    def init():
        load_dotenv()
        if "PRIVATE_KEY" not in os.environ or "PUBLIC_KEY" not in os.environ:
            key = RSA.generate(2048)
            priv = key.export_key().decode('utf-8')
            pub = key.public_key().export_key().decode('utf-8')
            os.environ["PRIVATE_KEY"] = priv
            os.environ["PUBLIC_KEY"] = pub
            with open(".env", "a") as env:
                env.writelines([f"PRIVATE_KEY=\"{priv}\"", "\n", f"PUBLIC_KEY=\"{pub}\""])

    @staticmethod
    def get(key: str, default=None, required: bool = True) -> str:
        val = os.getenv(key, default)
        if not val and required:
            raise EnvironmentError(f"could not find required environment variable {key}")
        return val

    @staticmethod
    def get_bool(key: str, required: bool = True) -> bool:
        return Env.get(key, "False", required).lower() in ('true', '1', 't')

    @staticmethod
    def get_int(key: str, required: bool = True):
        try:
            return int(Env.get(key, required=required))
        except ValueError:
            return None

    @staticmethod
    def get_admins() -> list:
        return [admin.strip().lower() for admin in Env.get("ADMINS").split(",")]

    @staticmethod
    def get_openid_config():
        return {
            "issuer": Env.get("PUBLIC_URL"),
            "authorization_endpoint": f"{Env.get('PUBLIC_URL')}/oauth/authorize",
            "token_endpoint": f"{Env.get('PUBLIC_URL')}/oauth/token",
            "revocation_endpoint": f"{Env.get('PUBLIC_URL')}/oauth/revoke",
            "userinfo_endpoint": f"{Env.get('PUBLIC_URL')}/userinfo",
            "jwks_uri": f"{Env.get('PUBLIC_URL')}/.well-known/jwks",
            "id_token_signing_alg_values_supported": "RS256",
            "subject_types_supported": ["public"],
            "response_types_supported": ["code"],
            "introspection_endpoint": None
        }
