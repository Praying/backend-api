from pydantic import BaseModel
from typing import List

class TradingPairBase(BaseModel):
    exchange_name: str
    trading_pairs: List[str]

class TradingPairCreate(TradingPairBase):
    pass

class TradingPair(TradingPairBase):
    class Config:
        from_attributes = True