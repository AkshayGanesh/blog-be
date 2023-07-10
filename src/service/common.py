from fastapi import APIRouter, Depends

from src.handlers.common import CommonHandler
from src.utils.security_utils.decorators import CookieAuthentication

app = APIRouter(tags=["Common"])

auth = CookieAuthentication()
handler = CommonHandler()

@app.get("/welcome/nav")
def get_user_info(
    email=Depends(auth),
):
    return handler.get_user_info(
        email=email,
    )
