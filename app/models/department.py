import uuid
from sqlalchemy import Column, String, Integer, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pid = Column(UUID(as_uuid=True), nullable=True)
    name = Column(String, nullable=False)
    status = Column(Integer, default=1)
    createTime = Column(DateTime, default=func.now())
    remark = Column(String)