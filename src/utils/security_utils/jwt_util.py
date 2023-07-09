import jwt
from jwt.exceptions import (
    InvalidSignatureError,
    ExpiredSignatureError,
    MissingRequiredClaimError,
)

from src.common import exceptions
from loguru import logger

class KeyPath:
    public = "assets/keys/public"
    private = "assets/keys/private"


class Secrets:
    LOCK_OUT_TIME_MINS = 30
    leeway_in_mins = 10
    unique_key = '45c37939-0f75'
    token = '8674cd1d-2578-4a62-8ab7-d3ee5f9a'
    issuer = "ilens"
    alg = "RS256"
    SECRET_FOR_SUPPORT_LENS = "WeSupport24X7UnifyTwinX#"
    ISS = "unifytwin"
    AUD = "supportlens"

class JWT:
    def __init__(self):
        self.max_login_age = 3600
        self.issuer = Secrets.issuer
        self.alg = Secrets.alg
        self.public = KeyPath.public
        self.private = KeyPath.private

    def encode(self, payload):
        try:
            with open(self.private, "r") as f:
                key = f.read()
            return jwt.encode(payload, key, algorithm=self.alg)
        except Exception as e:
            logger.exception(f'Exception while encoding JWT: {str(e)}')
            raise
        finally:
            f.close()

    def validate(self, token):
        try:
            with open(self.public, "r") as f:
                key = f.read()
            payload = jwt.decode(
                token,
                key,
                algorithms=self.alg,
                leeway=Secrets.leeway_in_mins,
                options={"require": ["exp", "iss"]},
            )
            return payload
        except InvalidSignatureError:
            raise exceptions.AuthenticationError(exceptions.ErrorMessages.ERROR003)
        except ExpiredSignatureError:
            raise exceptions.AuthenticationError(exceptions.ErrorMessages.ERROR002)
        except MissingRequiredClaimError:
            raise exceptions.AuthenticationError(exceptions.ErrorMessages.ERROR002)
        except Exception as e:
            logger.exception(f'Exception while validating JWT: {str(e)}')
            raise
        finally:
            f.close()

    @staticmethod
    def create_jwt_for_support_lens(payload):
        try:
            encoded_jwt = jwt.encode(payload, Secrets.SECRET_FOR_SUPPORT_LENS, algorithm="HS256")
            return encoded_jwt
        except Exception as e:
            logger.exception(f'Exception while encoding JWT: {str(e)}')
            raise
