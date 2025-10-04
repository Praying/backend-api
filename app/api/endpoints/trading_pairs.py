from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import dependencies
from app.crud import get_trading_pair_by_exchange
from app.schemas import TradingPair

router = APIRouter()

@router.get("/{exchange_name}")
async def read_trading_pairs(
    exchange_name: str,
    db: AsyncSession = Depends(dependencies.get_db),
):
    try:
        db_trading_pair = await get_trading_pair_by_exchange(db, exchange_name=exchange_name)
        if db_trading_pair is None:
            raise HTTPException(status_code=404, detail="Exchange not found")
        return {"code": 0, "data": db_trading_pair, "message": "ok"}
    except Exception as e:
        # In a real application, you'd want to log the error e
        raise HTTPException(status_code=500, detail="Internal Server Error")