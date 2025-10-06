import os
import json
import asyncio
import shlex
import shutil
from pathlib import PurePath
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.v6_single_backtest import V6SingleBacktest
from app.schemas.v6_single_backtest import V6SingleBacktestCreate, V6SingleBacktestUpdate
from sqlalchemy.inspection import inspect
from datetime import datetime
from app.crud.preference import get_preference

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
    backtest_name = backtest.name
    # 1. Ensure the queue directory exists
    backtest_dir = f"data/bt_v6_single_queue/{backtest_name}"
    os.makedirs(backtest_dir, exist_ok=True)

    # 2. Write config to a JSON file
    
    json_path = os.path.join(backtest_dir, f"{backtest_name}.json")
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
    backtest = await get_v6_single_backtest(db, backtest_id)
    if backtest:
        backtest_dir = f"data/bt_v6_single_queue/{backtest.name}"
        if os.path.exists(backtest_dir):
            shutil.rmtree(backtest_dir)
            
    q = delete(V6SingleBacktest).where(V6SingleBacktest.id == backtest_id)
    result = await db.execute(q)
    
    if result.rowcount == 0:
        return {"ok": False, "message": "Backtest not found"}

    await db.commit()
    return {"ok": True}

async def update_backtest_status(db: AsyncSession, backtest_id: int, status: str):
    """
    Helper function to update the status of a backtest.
    """
    q = update(V6SingleBacktest).where(V6SingleBacktest.id == backtest_id).values(status=status)
    await db.execute(q)
    await db.commit()
    return await get_v6_single_backtest(db, backtest_id)

async def run_backtest_process(db: AsyncSession, backtest_id: int):
    """
    Runs a backtest as a background process, updating its status upon completion.
    """
    # 1. Get the backtest record
    backtest = await get_v6_single_backtest(db, backtest_id)
    if not backtest:
        # Optionally log this error
        return
    # 2. Ensure the queue and log directories exist
    backtest_dir = f"data/bt_v6_single_queue/{backtest.name}"
    os.makedirs(backtest_dir, exist_ok=True)



    # 3. Set status to 'RUNNING'
    await update_backtest_status(db, backtest_id, "running")

    try:
        preference = await get_preference(db)
        pb6venv = preference.pbv6_interpreter_path if preference else None
        pb6dir = preference.pbv6_path if preference else None

        if not pb6venv or not pb6dir:
            raise ValueError("Interpreter path or Passivbot v6 path not configured in preferences.")

        # 4. Define file paths
        file_name = backtest.name
        cfg_path = os.path.abspath(os.path.join(backtest_dir, f"{file_name}.json"))
        log_path = os.path.abspath(os.path.join(backtest_dir, f"{file_name}.log"))

        # 5. Run the backtest process asynchronously
        cmd = [pb6venv, '-u', str(PurePath(f'{pb6dir}/backtest.py'))]
        cmd_end = f'-dp -u {backtest.account_name} -s {backtest.symbol} -sd {backtest.start_date.strftime("%Y-%m-%d")} -ed {backtest.end_date.strftime("%Y-%m-%d")} -sb {backtest.initial_capital} -m {backtest.market_type}'
        cmd.extend(shlex.split(cmd_end))
        #cmd.extend(['-bd', str(PurePath(f'{pb6dir}/backtests/pbgui')), str(PurePath(cfg_path))])
        cmd.extend(['-bd', str(PurePath(os.path.abspath(backtest_dir))), str(PurePath(cfg_path))])

        
        with open(log_path, "w") as log_file:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=log_file,
                stderr=log_file,
                cwd=pb6dir
            )
            
            return_code = await process.wait()

        # 6. Update status based on return code
        final_status = "finished" if return_code == 0 else "failed"
        await update_backtest_status(db, backtest_id, final_status)

    except Exception as e:
        # On any exception, mark as 'failed'
        print(f"Error running backtest {backtest_id}: {e}") # Or use a proper logger
        await update_backtest_status(db, backtest_id, "failed")