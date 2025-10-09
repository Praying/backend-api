from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.coinmarket import CoinMarketCap
from app.schemas.coinmarket import CoinMarketCapCreate

async def get_coinmarket(db: AsyncSession):
    result = await db.execute(select(CoinMarketCap))
    return result.scalars().first()

async def create_or_update_coinmarket(db: AsyncSession, coinmarket: CoinMarketCapCreate):
    db_coinmarket = await get_coinmarket(db)
    if db_coinmarket:
        # Update existing record
        db_coinmarket.coin_market_cap_api_key = coinmarket.coin_market_cap_api_key
        db_coinmarket.fetch_limit = coinmarket.fetch_limit
        db_coinmarket.fetch_interval = coinmarket.fetch_interval
        db_coinmarket.metadata_interval = coinmarket.metadata_interval
    else:
        # Create new record
        db_coinmarket = CoinMarketCap(
            coin_market_cap_api_key=coinmarket.coin_market_cap_api_key,
            fetch_limit=coinmarket.fetch_limit,
            fetch_interval=coinmarket.fetch_interval,
            metadata_interval=coinmarket.metadata_interval
        )
        db.add(db_coinmarket)

    await db.commit()
    await db.refresh(db_coinmarket)
    return db_coinmarket