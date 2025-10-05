from app.database.session import engine
from app.database.base import Base
from app.models.user import User
from app.models.department import Department
from app.models.api_key import ApiKey
from app.models.v6_single_backtest import V6SingleBacktest
from app.crud.user import get_user_by_username, create_user
from app.schemas.user import UserCreate
from app.database.session import SessionLocal
from app.crud.trading_pair import get_trading_pair_by_exchange, create_trading_pair
from app.schemas.trading_pair import TradingPairCreate

async def init_db():
    async with engine.begin() as conn:
#        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as db:
        user = await get_user_by_username(db, "vben")
        if not user:
            user_in = UserCreate(username="vben", password="123456", roles=["Super"])
            await create_user(db, user_in)

        exchanges = [
            "binance_futures", "binance_spot", "bybit_futures", "bybit_spot",
            "bitget_futures", "bitget_spot", "okx_futures", "okx_spot"
        ]
        trading_pairs = [
            "BTCUSDT", "BNBUSDT", "ETHUSDT", "XRPUSDT",
            "DOGEUSDT", "SOLUSDT", "TRXUSDT"
        ]
        for exchange in exchanges:
            db_trading_pair = await get_trading_pair_by_exchange(db, exchange)
            if not db_trading_pair:
                trading_pair_in = TradingPairCreate(exchange_name=exchange, trading_pairs=trading_pairs)
                await create_trading_pair(db, trading_pair_in)