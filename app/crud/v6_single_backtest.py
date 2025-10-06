import os
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.v6_single_backtest import V6SingleBacktest
from app.schemas.v6_single_backtest import V6SingleBacktestCreate, V6SingleBacktestUpdate
from sqlalchemy.inspection import inspect
from datetime import datetime

def _to_dict(obj):
    """
    Convert a SQLAlchemy model instance to a dictionary.
    """
    if obj is None:
        return None
    
    data = {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
    return data

async def create_v6_single_backtest(db: AsyncSession, backtest: V6SingleBacktestCreate):
    # 1. Ensure the queue directory exists
    queue_dir = "data/bt_v6_single_queue"
    os.makedirs(queue_dir, exist_ok=True)

    # 2. Write config to a JSON file
    file_name = backtest.name
    json_path = os.path.join(queue_dir, f"{file_name}.json")
    with open(json_path, 'w') as f:
        json.dump(backtest.config, f, indent=4)

    # 3. Create backtest record in the database
    backtest_data = backtest.dict()
    del backtest_data['config']
    db_backtest = V6SingleBacktest(**backtest_data)
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

async def start_backtest(db: AsyncSession, backtest_id: int):
    """
    Starts a backtest by creating configuration files and updating its status.
    """
    # 1. Ensure the queue directory exists
    queue_dir = "data/bt_v6_single_queue"
    os.makedirs(queue_dir, exist_ok=True)

    # 2. Get the backtest record
    backtest = await get_v6_single_backtest(db, backtest_id)
    if not backtest:
        return None

    # 3. Write backtest info to a JSON file
    file_name = backtest.name
    json_path = os.path.join(queue_dir, f"{file_name}.json")
    cfg_path = os.path.join(queue_dir, f"{file_name}.json.cfg")

    backtest_dict = _to_dict(backtest)

    with open(json_path, 'w') as f:
        json.dump(backtest_dict, f, indent=4)

    # 4. Create an empty .cfg file
    with open(cfg_path, 'w') as f:
        json.dump({}, f)

    # 5. Update the backtest status to 'RUNNING'
    q = update(V6SingleBacktest).where(V6SingleBacktest.id == backtest_id).values(status="RUNNING")
    await db.execute(q)
    await db.commit()

    return await get_v6_single_backtest(db, backtest_id)