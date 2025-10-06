import os
from fastapi import FastAPI
from app.api.endpoints import auth, user, system, trading_pairs, v6_single_backtest, preference
from app.database.init_db import init_db

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    # Ensure the data directory exists
    os.makedirs("data", exist_ok=True)
    await init_db()

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(system.router)
app.include_router(trading_pairs.router, prefix="/api/trading-pairs", tags=["trading-pairs"])
app.include_router(v6_single_backtest.router, prefix="/api/v6-single/backtest", tags=["v6-single-backtest"])
app.include_router(preference.router, prefix="/api/system/preferences", tags=["preferences"])
# Trigger reload