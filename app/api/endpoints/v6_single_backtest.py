from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
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