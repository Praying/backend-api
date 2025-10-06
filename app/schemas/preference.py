from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PreferenceBase(BaseModel):
    pbv6_path: Optional[str] = None
    pbv6_interpreter_path: Optional[str] = None
    pbv7_path: Optional[str] = None
    pbv7_interpreter_path: Optional[str] = None

    class Config:
        allow_population_by_field_name = True

class PreferenceCreate(PreferenceBase):
    pass

class PreferenceUpdate(PreferenceBase):
    pass

class Preference(PreferenceBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True