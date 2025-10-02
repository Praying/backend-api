from pydantic import BaseModel
from typing import List
import uuid

class UserBase(BaseModel):
    username: str
    roles: List[str] = []

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

class UserInfoResponse(BaseModel):
    code: int
    data: User
    message: str

    class Config:
        from_attributes = True