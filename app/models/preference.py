from sqlalchemy import Column, Integer, String, DateTime, func
from app.database.base import Base

class Preference(Base):
    __tablename__ = "preferences"

    id = Column(Integer, primary_key=True, index=True, default=1)
    pbv6_path = Column(String(255), nullable=True)
    pbv6_interpreter_path = Column(String(255), nullable=True)
    pbv7_path = Column(String(255), nullable=True)
    pbv7_interpreter_path = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())