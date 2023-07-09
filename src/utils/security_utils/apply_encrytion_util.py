import uuid
from datetime import timedelta, datetime

from src.utils.security_utils.jwt_util import JWT
from src.utils import redis_util

jwt = JWT()

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

def create_token(user_id, ip, token, age=30, login_token=None):
    """
    This method is to create a cookie
    """
    try:
        uid = login_token
        if not uid:
            uid = str(uuid.uuid4()).replace("-", "")

        payload = {
            "ip": ip,
            "user_id": user_id,
            "token": token,
            "uid": uid,
            "age": age
        }

        exp = datetime.utcnow() + timedelta(minutes=age)
        _extras = {"iss": Secrets.issuer, "exp": exp}
        _payload = {**payload, **_extras}

        new_token = jwt.encode(_payload)

        # Add session to redis
        redis_util.set_user_token(
            uid=uid,
            token=new_token,
            age_in_seconds=60 * age,
        )

        return uid
    except Exception:
        raise
