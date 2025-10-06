from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import dependencies
from app.crud import preference as crud_preference
from app.schemas import preference as schemas_preference

router = APIRouter()

@router.get("/")
async def read_preference(db: AsyncSession = Depends(dependencies.get_db)):
    db_preference = await crud_preference.get_preference(db)
    if db_preference is None:
        return {"code": 0, "data": {}, "message": "ok"}
    return {"code": 0, "data": db_preference, "message": "ok"}

@router.post("/")
async def create_or_update_preference(
    *,
    db: AsyncSession = Depends(dependencies.get_db),
    preference_in: schemas_preference.PreferenceCreate
):
    preference = await crud_preference.create_or_update_preference(db=db, preference=preference_in)
    return {"code": 0, "data": preference, "message": "ok"}