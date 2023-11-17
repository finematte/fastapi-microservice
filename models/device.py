from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base


class Device(Base):
    __tablename__ = "devices"
    device_id = Column(Integer, primary_key=True, index=True)
    user_login = Column(String, ForeignKey("users.user_login"))
    name = Column(String)
    user = relationship("User", back_populates="devices")
    tasks = relationship("Task", back_populates="device")
    data = relationship("Data", back_populates="device")
    historical_data = relationship("HistoricalData", back_populates="device")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
