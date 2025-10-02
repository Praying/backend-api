from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserInfoResponse

router = APIRouter()

@router.get("/api/user/info", response_model=UserInfoResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "code": 0,
        "data": current_user,
        "message": "ok",
    }