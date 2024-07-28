from pydantic import BaseModel


class UserUpdateModel(BaseModel):
    username: str
    user_role: str
    user_id: str
