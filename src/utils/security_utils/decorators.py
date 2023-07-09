from secrets import compare_digest

from fastapi import Response, Request, HTTPException
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security import APIKeyCookie
from fastapi.security.api_key import APIKeyBase

from src.utils import redis_util
from src.utils.security_utils.apply_encrytion_util import create_token
from src.utils.security_utils.jwt_util import JWT

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

class CookieAuthentication(APIKeyBase):
    """
    Authentication backend using a cookie.
    Internally, uses a JWT token to store the data.
    """

    scheme: APIKeyCookie
    cookie_name: str
    cookie_secure: bool

    def __init__(
            self,
            cookie_name: str = "login-token",
    ):
        super().__init__()
        self.model: APIKey = APIKey(**{"in": APIKeyIn.cookie}, name=cookie_name)
        self.scheme_name = self.__class__.__name__
        self.cookie_name = cookie_name
        self.scheme = APIKeyCookie(name=self.cookie_name, auto_error=False)
        self.jwt = JWT()

    async def __call__(self, request: Request, response: Response) -> HTTPException | str:
        cookies = request.cookies
        login_token = cookies.get("login-token")
        if not login_token:
            login_token = request.headers.get("login-token")

        if not login_token:
            return HTTPException(status_code=401)

        jwt_token = redis_util.get_user_token(login_token)
        if not jwt_token:
            return HTTPException(status_code=401)

        try:
            decoded_token = self.jwt.validate(token=jwt_token)
            if not decoded_token:
                return HTTPException(status_code=401)
        except Exception as e:
            return HTTPException(status_code=401, detail=e.args)

        user_id = decoded_token.get("user_id")

        _token = decoded_token.get("token")
        _age = int(decoded_token.get("age", 60))

        if not compare_digest(Secrets.token, _token):
            return HTTPException(status_code=401)
        if login_token != decoded_token.get("uid"):
            return HTTPException(status_code=401)

        try:
            new_token = create_token(
                user_id=user_id,
                ip=request.client.host,
                token=Secrets.token,
                age=_age,
                login_token=login_token
            )
        except Exception as e:
            return HTTPException(status_code=401, detail=e.args)
        response.set_cookie(
            'login-token',
            new_token,
            samesite='strict',
            httponly=True,
            max_age=60 * 60,
            secure=True
        )
        response.headers['login-token'] = new_token

        return user_id
