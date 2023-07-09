from typing import Optional

from pydantic import BaseModel


class UserRegistrationModel(BaseModel):
    name: str
    email: str
    password: str


class UserLoginRequest(BaseModel):
    email: str
    password: str
    max_age: int = 30
    project_id: Optional[str] = ""