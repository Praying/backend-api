from pydantic import BaseModel
from typing import List
import uuid

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserInfo(BaseModel):
    id: uuid.UUID
    username: str
    roles: List[str]
    accessToken: str

class LoginResponse(BaseModel):
    code: int
    data: UserInfo
    message: str

class PermissionCodesData(BaseModel):
    codes: List[str]

class PermissionCodesResponse(BaseModel):
    code: int
    data: PermissionCodesData
    message: str