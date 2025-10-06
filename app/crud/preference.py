from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.preference import Preference
from app.schemas.preference import PreferenceCreate

async def get_preference(db: AsyncSession):
    result = await db.execute(select(Preference).filter(Preference.id == 1))
    return result.scalars().first()

async def create_or_update_preference(db: AsyncSession, preference: PreferenceCreate):
    db_preference = await get_preference(db)
    if db_preference:
        update_data = preference.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_preference, key, value)
        db.add(db_preference)
        await db.commit()
        await db.refresh(db_preference)
        return db_preference
    else:
        db_preference = Preference(**preference.dict(), id=1)
        db.add(db_preference)
        await db.commit()
        await db.refresh(db_preference)
        return db_preference
