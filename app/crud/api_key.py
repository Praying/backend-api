from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.api_key import ApiKey
from app.schemas.api_key import ApiKeyCreate, ApiKey as ApiKeySchema

async def get_api_keys(db: AsyncSession):
    result = await db.execute(select(ApiKey))
    return result.scalars().all()

async def create_api_key(db: AsyncSession, api_key: ApiKeyCreate):
    db_api_key = ApiKey(**api_key.dict())
    db.add(db_api_key)
    await db.commit()
    await db.refresh(db_api_key)
    return db_api_key

async def get_api_key(db: AsyncSession, id: int):
    result = await db.execute(select(ApiKey).filter(ApiKey.id == id))
    return result.scalars().first()

async def update_api_key(db: AsyncSession, db_obj: ApiKey, obj_in: ApiKeyCreate):
    update_data = obj_in.dict(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_api_key(db: AsyncSession, id: int):
    result = await db.execute(select(ApiKey).filter(ApiKey.id == id))
    db_obj = result.scalars().first()
    if db_obj:
        await db.delete(db_obj)
        await db.commit()
    return db_obj