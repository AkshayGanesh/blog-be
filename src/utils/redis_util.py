import json

from typing import Optional

import redis

from src.common import exceptions

class Redis_Config:
    redis_data_uri: str = "redis://localhost:6379/2"
    redis_login_uri: str = "redis://localhost:6379/3"

class RedisConnection:
    def __init__(self, uri):
        self.connection = redis.Redis.from_url(
            url=uri,
            decode_responses=True)

    def get_connection(self):
        return self.connection

redis_data_db = RedisConnection(uri=Redis_Config.redis_data_uri).get_connection()
redis_login_db = RedisConnection(uri=Redis_Config.redis_login_uri).get_connection()

def insert_one_article(
    article_id: str,
    article_data: str,
):
    redis_data_db.hset(
        "blog:articles",
        article_id,
        json.dumps(article_data),
    )

def delete_one_article(
    article_id: str,
):
    redis_data_db.hdel(
        "blog:articles",
        article_id,
    )

def retrive_articles(
    article_id: Optional[str] = None,
):
    if article_id:
        _article_data = redis_data_db.hget(
            "blog:articles",
            article_id,
        )
        if _article_data:
            return json.loads(_article_data)
        return {}
    
    _article_data = redis_data_db.hgetall(
        "blog:articles",
    )
    if _article_data:
        _decoded_response = {}
        for key, value in _article_data.items():
            _decoded_response[key] = json.loads(value)
        return _decoded_response
    return {}

def add_user(
    name: str,
    email: str,
    enc_password: str,
    doj: str,
):
    if redis_data_db.hget(
        "blog:users:user",
        email,
    ):
        raise exceptions.UserAlreadyExist(f"User {name} with email {email} already exist!")
    
    redis_data_db.hset(
        "blog:users:user",
        email,
        json.dumps({
            "name": name,
            "email": email,
            "enc_password": enc_password,
            "doj": doj,
        })
    )

def get_user(
    email: str,
):
    user_data = redis_data_db.hget(
        "blog:users:user",
        email,
    )
    if not user_data:
        raise exceptions.UserDoesNotExist(f"User with email {email} does not exist!")
    return json.loads(user_data)

def set_user_token(
    uid: str, 
    token: str,
    age_in_seconds: int = 3600, 
):
    with redis_login_db.pipeline() as pipe:
        pipe.set(
            uid,
            token,
        )
        pipe.expire(
            uid,
            age_in_seconds,
        )
        pipe.execute()

def get_user_token(
    login_token: str,
):
    return redis_login_db.get(
        login_token
    )

def delete_token(
    token: str,
):
    if token:
        return redis_login_db.delete(
            token
        )