from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

import uuid

async def get_user_by_id(db: AsyncSession, user_id: str):
    try:
        val_uuid = uuid.UUID(user_id, version=4)
    except ValueError:
        return None
    result = await db.execute(select(User).filter(User.id == val_uuid))
    return result.scalars().first()
from app.schemas.user import UserCreate
from app.security import get_password_hash

async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password, roles=user.roles)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user