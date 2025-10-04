from sqlalchemy import Column, String, JSON
from app.database.base import Base

class TradingPair(Base):
    __tablename__ = "trading_pairs"

    exchange_name = Column(String, primary_key=True, index=True)
    trading_pairs = Column(JSON, nullable=False)