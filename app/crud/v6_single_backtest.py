from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.v6_single_backtest import V6SingleBacktest
from app.schemas.v6_single_backtest import V6SingleBacktestCreate, V6SingleBacktestUpdate

async def create_v6_single_backtest(db: AsyncSession, backtest: V6SingleBacktestCreate):
    db_backtest = V6SingleBacktest(**backtest.dict())
    db.add(db_backtest)
    await db.commit()
    await db.refresh(db_backtest)
    return db_backtest

async def get_v6_single_backtest(db: AsyncSession, backtest_id: int):
    result = await db.execute(select(V6SingleBacktest).filter(V6SingleBacktest.id == backtest_id))
    return result.scalars().first()

async def get_v6_single_backtests(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(V6SingleBacktest).offset(skip).limit(limit))
    return result.scalars().all()

async def update_v6_single_backtest(db: AsyncSession, backtest_id: int, backtest: V6SingleBacktestUpdate):
    update_data = backtest.dict(exclude_unset=True)
    if not update_data:
        return None
    q = update(V6SingleBacktest).where(V6SingleBacktest.id == backtest_id).values(**update_data)
    await db.execute(q)
    await db.commit()
    return await get_v6_single_backtest(db, backtest_id)

async def delete_v6_single_backtest(db: AsyncSession, backtest_id: int):
    q = delete(V6SingleBacktest).where(V6SingleBacktest.id == backtest_id)
    await db.execute(q)
    await db.commit()
    return {"ok": True}