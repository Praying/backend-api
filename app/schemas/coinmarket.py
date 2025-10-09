from pydantic import BaseModel

class CoinMarketCapBase(BaseModel):
    coin_market_cap_api_key: str
    fetch_limit: int
    fetch_interval: int
    metadata_interval: int

class CoinMarketCapCreate(CoinMarketCapBase):
    pass

class CoinMarketCapUpdate(CoinMarketCapBase):
    pass

class CoinMarketCapInDBBase(CoinMarketCapBase):
    id: int

    class Config:
        from_attributes = True

class CoinMarketCap(CoinMarketCapInDBBase):
    pass