from fastapi.responses import JSONResponse

from src.utils import redis_util


class CommonHandler:
    
    @staticmethod
    def get_user_info(
        email
    ):
        response = {"name": None}
        if isinstance(email, str):
            response["name"] = redis_util.get_user(email=email).get("name")
        return JSONResponse(content=response)
