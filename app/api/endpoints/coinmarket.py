from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, schemas
from app.api import dependencies

router = APIRouter()

@router.get("")
async def read_coinmarket_config(db: AsyncSession = Depends(dependencies.get_db)):
    db_coinmarket = await crud.coinmarket.get_coinmarket(db)
    if not db_coinmarket:
        db_coinmarket = {
            "coin_market_cap_api_key": "",
            "fetch_limit": 5000,
            "fetch_interval": 24,
            "metadata_interval": 1,
            "id": 0
        }
    return {
        "code": 0,
        "data": db_coinmarket,
        "message": "ok"
    }

@router.post("")
async def create_or_update_coinmarket_config(
    *,
    db: AsyncSession = Depends(dependencies.get_db),
    coinmarket_in: schemas.CoinMarketCapCreate,
):
    await crud.coinmarket.create_or_update_coinmarket(db=db, coinmarket=coinmarket_in)
    return {
        "code": 0,
        "data": None,
        "message": "Configuration saved successfully."
    }