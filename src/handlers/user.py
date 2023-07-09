import datetime
from fastapi import Response, Request
from loguru import logger
from fastapi.responses import JSONResponse

from src.common.settings import config
from src.schemas.user import UserLoginRequest
from src.utils.security_utils.aes_enc import AESCipher
from src.utils.security_utils.apply_encrytion_util import create_token
from src.schemas.user import UserRegistrationModel
from src.utils import redis_util
from src.common import exceptions


class UserHandler:
    def get_token(self, response: Response, t: str = None):
        response.set_cookie('token', config.permanent_token)
        response = {
            "token": config.permanent_token,
            "status": "success"}
        return response
    
    def login(
            self, 
            login_request: UserLoginRequest, 
            request: Request, 
            response: Response, 
            token: str, enc=True,
        ):
        try:            
            user_record = redis_util.get_user(email=login_request.email)

            auth = self.validate_password(
                password=login_request.password,
                user_record=user_record,
                token=token,
                enc=enc,
            )
            if not auth:
                return False

            client_ip = request.client.host
            refresh_age = config.refresh_token_duration
            refresh_token = create_token(
                user_id=user_record.get("email"),
                ip=client_ip,
                token=token,
                age=refresh_age * 60
            )

            response.set_cookie(
                'refresh-token',
                refresh_token,
                samesite='strict',
                httponly=True,
                max_age=refresh_age * 60 * 60,
                secure=True
            )
            response.set_cookie(
                'login-token',
                refresh_token,
                samesite='strict',
                httponly=True,
                max_age=refresh_age * 60 * 60,
                secure=True
            )

            response.headers['refresh-token'] = refresh_token

            return {"email": user_record["email"], "name": user_record["name"]}
        except exceptions.InvalidPasswordError:
            logger.exception("Failed to login! Incorrect Password!")
            return False
        except exceptions.UserDoesNotExist:
            logger.exception("Failed to login! User unauthorised!")
            return False
        except Exception as e:
            logger.exception(str(e))
            return False
        
    
    def validate_password(self, password, user_record, token, enc):
        if token != config.permanent_token:
            raise ValueError(msg="Invalid token!")
        if enc:
            password = AESCipher().decrypt(password)
        
        if not password == AESCipher().decrypt(user_record['enc_password']):
            logger.error(f"{password} does not match {user_record['enc_password']}")
            raise ValueError("Failed to login! Incorrect password")
        
        return True
    
    def register_user(
        self,
        user: UserRegistrationModel,
        enc=True,
    ):
        try:
            if not enc:
                raise ValueError("Passwords should be encrypted!")

            redis_util.add_user(
                name=user.name,
                email=user.email,
                enc_password=user.password,
                doj=datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            )
            return user.name
        except Exception as e:
            logger.exception(str(e))
            return {"status": "failed", "message": str(e)}
        
    def logout(
            self,
            request: Request,
        ) -> JSONResponse:
        login_token = request.cookies.get("login-token")
        if login_token is None:
            login_token = request.headers.get("login-token")
        refreshToken = request.cookies.get("refresh-token")
        if refreshToken is None:
            refreshToken = request.headers.get("refresh-token")

        resp = JSONResponse({"status": True, "message": "Logout Successfully"})
        resp.set_cookie("session_id", "", expires=0)
        resp.set_cookie("user_id", "", expires=0)
        resp.set_cookie("login-token", "", expires=0)
        resp.set_cookie("userId", "", expires=0)
        resp.set_cookie("refresh-token", "", expires=0)
        resp.set_cookie("token", "", expires=0)
        redis_util.delete_token(login_token)
        redis_util.delete_token(refreshToken)
        return resp
