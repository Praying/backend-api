from sqlalchemy import Column, Integer, String
from app.database.base import Base

class CoinMarketCap(Base):
    __tablename__ = "coinmarketcap"

    id = Column(Integer, primary_key=True, index=True)
    coin_market_cap_api_key = Column(String, index=True)
    fetch_limit = Column(Integer)
    fetch_interval = Column(Integer)
    metadata_interval = Column(Integer)