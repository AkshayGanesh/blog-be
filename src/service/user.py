from typing import Optional
from fastapi import APIRouter, Response, Request, Cookie, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger

from src.handlers.user import UserHandler
from src.schemas import user as user_schema


app = APIRouter(tags=["User"], prefix="/api")
handler = UserHandler()


@app.post("/auth/register")
def register_user(
    user: user_schema.UserRegistrationModel,
    request: Request,
    response: Response,
    token: str = Cookie(...),
):
    try:
        response = handler.register_user(
            user=user,
            enc=True
        )
        return {"status": True, "data": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=e.args, )

@app.post("/auth/login")
def login(
        login_request: user_schema.UserLoginRequest,
        request: Request,
        response: Response,
        token: str = Cookie(...),
):
    try:
        response = handler.login(
            login_request=login_request,
            request=request,
            response=response,
            token=token,
        )
        if bool(response):
            return response
        else:
            return JSONResponse(content={"status": False, "data": "Failed to login! User unauthorised!"},status_code=401)
    except Exception as e:
        raise HTTPException(status_code=401, detail=e.args, )


@app.post("/auth/logout")
def login(
        request: Request,
):
    try:
        response = handler.logout(
            request=request,
        )
        return response
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=401, detail=e.args, )
    

@app.get("/auth/token")
def get_token(
    response: Response,
    t: Optional[str] = None
):
    return handler.get_token(response, t=t)


