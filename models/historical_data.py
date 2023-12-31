from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base


class HistoricalData(Base):
    __tablename__ = "historical_data"
    historical_data_id = Column(Integer, primary_key=True)
    device_id = Column(String, ForeignKey("devices.device_id"))
    temp = Column(Float)
    soil_hum = Column(Float)
    air_hum = Column(Float)
    light = Column(Float)
    device = relationship("Device", back_populates="historical_data")
    created_at = Column(DateTime, default=datetime.utcnow)
