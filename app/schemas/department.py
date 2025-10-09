from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime

class DepartmentBase(BaseModel):
    name: str
    status: int
    remark: Optional[str] = None

class DepartmentCreate(DepartmentBase):
    pid: Optional[uuid.UUID] = None

class Department(DepartmentBase):
    id: uuid.UUID
    pid: Optional[uuid.UUID] = None
    createTime: datetime
    children: List['Department'] = []

    class Config:
        from_attributes = True

Department.update_forward_refs()

class DepartmentListResponse(BaseModel):
    code: int
    data: List[Department]
    message: str