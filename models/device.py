from sqlalchemy import Column, DateTime, VARCHAR, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base


class Device(Base):
    __tablename__ = "devices"
    device_id = Column(Integer, primary_key=True, index=True)
    tasks = relationship("Task", back_populates="device")
    data = relationship("Data", back_populates="device")
    historical_data = relationship("HistoricalData", back_populates="device")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
