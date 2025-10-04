from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.trading_pair import TradingPair
from app.schemas.trading_pair import TradingPairCreate

async def get_trading_pair_by_exchange(db: AsyncSession, exchange_name: str):
    result = await db.execute(select(TradingPair).filter(TradingPair.exchange_name == exchange_name))
    return result.scalars().first()

async def create_trading_pair(db: AsyncSession, trading_pair: TradingPairCreate):
    db_trading_pair = TradingPair(
        exchange_name=trading_pair.exchange_name,
        trading_pairs=trading_pair.trading_pairs
    )
    db.add(db_trading_pair)
    await db.commit()
    await db.refresh(db_trading_pair)
    return db_trading_pair