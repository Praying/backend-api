from sqlalchemy import Column, String, Integer, DateTime, Float
from app.database.base import Base
import uuid

class V6SingleBacktest(Base):
    __tablename__ = "v6_single_backtest"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    account_name = Column(String, index=True)
    exchange = Column(String)
    symbol = Column(String)
    market_type = Column(String)
    model = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    initial_capital = Column(Float)
    status = Column(String, default='CREATED')