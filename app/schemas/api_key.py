from pydantic import BaseModel, field_serializer
from typing import List, Optional
from datetime import datetime

class ApiKeyBase(BaseModel):
    exchange: str
    exchangeCategory: str
    accountName: str
    apiKey: str
    apiSecret: str
    passphrase: Optional[str] = None

class ApiKeyCreate(ApiKeyBase):
    pass

class ApiKey(ApiKeyBase):
    id: int
    status: Optional[str] = None
    createdAt: Optional[datetime] = None
    lastUpdatedAt: Optional[datetime] = None

    @field_serializer('createdAt', 'lastUpdatedAt')
    def serialize_dt(self, dt: datetime, _info):
        if dt is None:
            return None
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    class Config:
        from_attributes = True

class ApiKeyListResponse(BaseModel):
    code: int
    data: List[ApiKey]
    message: str