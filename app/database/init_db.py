from app.database.session import engine
from app.database.base import Base
from app.models.user import User
from app.models.department import Department
from app.models.api_key import ApiKey
from app.crud.user import get_user_by_username, create_user
from app.schemas.user import UserCreate
from app.database.session import SessionLocal

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as db:
        user = await get_user_by_username(db, "vben")
        if not user:
            user_in = UserCreate(username="vben", password="123456", roles=["Super"])
            await create_user(db, user_in)