from sqlalchemy import Column, String, Integer, DateTime
import datetime
from app.database.base import Base

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    exchange = Column(String, nullable=False)
    exchangeCategory = Column(String, nullable=False)
    accountName = Column(String, nullable=False)
    apiKey = Column(String, nullable=False)
    apiSecret = Column(String, nullable=False)
    passphrase = Column(String, nullable=True)
    createdAt = Column(DateTime, default=datetime.datetime.now)
    lastUpdatedAt = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)