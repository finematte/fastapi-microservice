from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base


class Data(Base):
    __tablename__ = "data"
    data_id = Column(Integer, primary_key=True)
    device_id = Column(String, ForeignKey("devices.device_id"), unique=True)
    temp = Column(Float)
    soil_hum = Column(Float)
    air_hum = Column(Float)
    light = Column(Float)
    device = relationship("Device", back_populates="data")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
