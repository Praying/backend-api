import os
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import json
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import dependencies
from app.crud import v6_single_backtest as crud
from app.schemas import v6_single_backtest as schemas

router = APIRouter()

@router.post("/")
async def create_v6_single_backtest(
    backtest: schemas.V6SingleBacktestCreate,
    db: AsyncSession = Depends(dependencies.get_db),
):
    result = await crud.create_v6_single_backtest(db=db, backtest=backtest)
    return {"code": 0, "data": result, "message": "ok"}

@router.get("/{backtest_id}")
async def read_v6_single_backtest(
    backtest_id: int,
    db: AsyncSession = Depends(dependencies.get_db),
):
    db_backtest = await crud.get_v6_single_backtest(db, backtest_id=backtest_id)
    if db_backtest is None:
        raise HTTPException(status_code=404, detail="Backtest not found")
    return {"code": 0, "data": db_backtest, "message": "ok"}

@router.get("/")
async def read_v6_single_backtests(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(dependencies.get_db),
):
    result = await crud.get_v6_single_backtests(db, skip=skip, limit=limit)
    return {"code": 0, "data": result, "message": "ok"}

@router.put("/{backtest_id}")
async def update_v6_single_backtest(
    backtest_id: int,
    backtest: schemas.V6SingleBacktestUpdate,
    db: AsyncSession = Depends(dependencies.get_db),
):
    db_backtest = await crud.update_v6_single_backtest(db, backtest_id=backtest_id, backtest=backtest)
    if db_backtest is None:
        raise HTTPException(status_code=404, detail="Backtest not found")
    return {"code": 0, "data": db_backtest, "message": "ok"}

@router.delete("/{backtest_id}")
async def delete_v6_single_backtest(
    backtest_id: int,
    db: AsyncSession = Depends(dependencies.get_db),
):
    result = await crud.delete_v6_single_backtest(db, backtest_id=backtest_id)
    if not result:
        raise HTTPException(status_code=404, detail="Backtest not found")
    return {"code": 0, "data": None, "message": "ok"}

@router.post("/{backtest_id}/start")
async def start_v6_single_backtest(
    backtest_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(dependencies.get_db),
):
    """
    Start a backtest task in the background.
    """
    db_backtest = await crud.get_v6_single_backtest(db, backtest_id=backtest_id)
    if db_backtest is None:
        raise HTTPException(status_code=404, detail="Backtest not found")

    # Check if the backtest is already running or starting
    if db_backtest.status in ["running", "starting"]:
        raise HTTPException(status_code=400, detail="Backtest is already running.")
    
    # Update status to 'starting' immediately
    await crud.update_backtest_status(db, backtest_id, "starting")
    
    # Add the long-running task to the background
    background_tasks.add_task(crud.run_backtest_process, db, backtest_id)
    
    return {"code": 0, "data": None, "message": "Backtest has been started in the background."}

@router.get("/{backtest_id}/log")
async def read_v6_single_backtest_log(
    backtest_id: int,
    db: AsyncSession = Depends(dependencies.get_db),
):
    """
    Retrieve the log file for a specific backtest.
    """
    db_backtest = await crud.get_v6_single_backtest(db, backtest_id=backtest_id)
    if db_backtest is None:
        raise HTTPException(status_code=404, detail="Backtest not found")

    log_path = crud.get_backtest_log_path(db_backtest)

    if not os.path.exists(log_path):
        raise HTTPException(status_code=404, detail="Log file not found")

    return FileResponse(log_path, media_type='text/plain', filename=f"{db_backtest.name}.log")

def get_plots_path(backtest: schemas.V6SingleBacktest) -> str | None:
    """
    Constructs the latest plots directory path for a given backtest.
    """
    base_path = f"data/bt_v6_single_queue/{backtest.name}"
    exchange_base = backtest.exchange.split('_')[0]
    plots_path = os.path.join(base_path, exchange_base, backtest.symbol, 'plots')

    if not os.path.isdir(plots_path):
        return None

    all_subdirs = [d for d in os.listdir(plots_path) if os.path.isdir(os.path.join(plots_path, d))]
    if not all_subdirs:
        return None

    latest_subdir = max(all_subdirs)
    return os.path.join(plots_path, latest_subdir)


@router.get("/{backtest_id}/stats")
async def get_backtest_stats(
    backtest_id: int,
    db: AsyncSession = Depends(dependencies.get_db),
):
    """
    Retrieve the statistics data for a specific backtest to render charts.
    """
    db_backtest = await crud.get_v6_single_backtest(db, backtest_id=backtest_id)
    if db_backtest is None:
        raise HTTPException(status_code=404, detail="Backtest not found")

    plots_dir = get_plots_path(db_backtest)
    if plots_dir is None:
        raise HTTPException(status_code=404, detail="Plots directory not found")
        
    csv_path = os.path.join(plots_dir, 'stats.csv')

    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Stats file not found")

    try:
        df = pd.read_csv(csv_path)
        json_data = df.to_dict(orient='records')
        return {"code": 0, "data": json_data, "message": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process stats file: {str(e)}")


@router.get("/{backtest_id}/result")
async def get_backtest_result(
    backtest_id: int,
    db: AsyncSession = Depends(dependencies.get_db),
):
    """
    Retrieve the backtest result text file for a specific backtest.
    """
    db_backtest = await crud.get_v6_single_backtest(db, backtest_id=backtest_id)
    if db_backtest is None:
        raise HTTPException(status_code=404, detail="Backtest not found")

    plots_dir = get_plots_path(db_backtest)
    if plots_dir is None:
        raise HTTPException(status_code=404, detail="Plots directory not found")
        
    result_path = os.path.join(plots_dir, 'backtest_result.txt')

    if not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="Result file not found")

    try:
        with open(result_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"code": 0, "data": content, "message": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process result file: {str(e)}")


@router.get("/{backtest_id}/config")
async def get_backtest_config(
    backtest_id: int,
    db: AsyncSession = Depends(dependencies.get_db),
):
    """
    Retrieve the configuration JSON file for a specific backtest.
    """
    db_backtest = await crud.get_v6_single_backtest(db, backtest_id=backtest_id)
    if db_backtest is None:
        raise HTTPException(status_code=404, detail="Backtest not found")

    config_path = f"data/bt_v6_single_queue/{db_backtest.name}/{db_backtest.name}.json"

    if not os.path.exists(config_path):
        raise HTTPException(status_code=404, detail="Config file not found")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        return {"code": 0, "data": config_data, "message": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process config file: {str(e)}")