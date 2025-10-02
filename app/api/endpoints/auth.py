from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.crud.user import get_user_by_username
from app.database.session import SessionLocal
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    PermissionCodesData,
    PermissionCodesResponse,
    UserInfo,
)
from app.security import create_access_token, verify_password


router = APIRouter()


async def get_db():
    async with SessionLocal() as session:
        yield session


@router.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_username(db, username=request.username)
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=403,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(subject=user.id)
    return LoginResponse(
        code=0,
        data=UserInfo(
            id=user.id,
            username=user.username,
            roles=user.roles,
            accessToken=access_token,
        ),
        message="ok",
    )


@router.get("/api/auth/codes", response_model=PermissionCodesResponse)
async def get_permission_codes(current_user: User = Depends(get_current_user)):
    """
    Get current user's permission codes.
    """
    return PermissionCodesResponse(
        code=0, data=PermissionCodesData(codes=current_user.roles), message="ok"
    )