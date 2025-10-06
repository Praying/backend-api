from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class V6SingleBacktestBase(BaseModel):
    config: Optional[dict] = None
    name: Optional[str] = None
    account_name: Optional[str] = None
    exchange: Optional[str] = None
    symbol: Optional[str] = None
    market_type: Optional[str] = None
    model: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    initial_capital: Optional[float] = None
    status: Optional[str] = None

class V6SingleBacktestCreate(V6SingleBacktestBase):
    config: dict
    name: str
    account_name: str
    exchange: str
    symbol: str
    market_type: str
    model: str
    start_date: datetime
    end_date: datetime
    initial_capital: float

class V6SingleBacktestUpdate(V6SingleBacktestBase):
    pass

class V6SingleBacktest(V6SingleBacktestBase):
    id: int

    class Config:
        orm_mode = True