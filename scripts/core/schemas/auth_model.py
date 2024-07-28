from typing import Optional

from pydantic import BaseModel, EmailStr


class UserModel(BaseModel):
    username: str
    password: str
    email: EmailStr
    user_role: Optional[str] = "developer"
    user_id: Optional[str] = ""


class LoginModel(BaseModel):
    username: str
    password: str
