import json
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.api_key import ApiKey
from app.schemas.api_key import ApiKeyCreate, ApiKey as ApiKeySchema
from app.crud.preference import get_preference

async def _sync_api_keys_to_json(db: AsyncSession):
    preference = await get_preference(db)
    if not preference or (not preference.pbv6_path and not preference.pbv7_path):
        return

    api_keys = await get_api_keys(db)
    api_keys_dict = {}
    for api_key in api_keys:
        api_key_data = {
            "exchange": api_key.exchange.split('_')[0],
            "key": api_key.apiKey,
            "secret": api_key.apiSecret
        }
        if api_key.passphrase:
            api_key_data["passphrase"] = api_key.passphrase
        api_keys_dict[api_key.accountName] = api_key_data

    paths_to_update = []
    if preference.pbv6_path and os.path.isdir(preference.pbv6_path):
        paths_to_update.append(os.path.join(preference.pbv6_path, 'api-keys.json'))
    if preference.pbv7_path and os.path.isdir(preference.pbv7_path):
        paths_to_update.append(os.path.join(preference.pbv7_path, 'api-keys.json'))

    for file_path in paths_to_update:
        with open(file_path, 'w') as f:
            json.dump(api_keys_dict, f, indent=4)

async def get_api_keys(db: AsyncSession):
    result = await db.execute(select(ApiKey))
    return result.scalars().all()

async def create_api_key(db: AsyncSession, api_key: ApiKeyCreate):
    db_api_key = ApiKey(**api_key.dict())
    db.add(db_api_key)
    await db.commit()
    await db.refresh(db_api_key)
    await _sync_api_keys_to_json(db)
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
    await _sync_api_keys_to_json(db)
    return db_obj

async def delete_api_key(db: AsyncSession, id: int):
    result = await db.execute(select(ApiKey).filter(ApiKey.id == id))
    db_obj = result.scalars().first()
    if db_obj:
        await db.delete(db_obj)
        await db.commit()
        await _sync_api_keys_to_json(db)
    return db_obj