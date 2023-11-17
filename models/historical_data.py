from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base


class HistoricalData(Base):
    __tablename__ = "historical_data"
    data_id = Column(Integer, primary_key=True)
    device_id = Column(
        Integer, ForeignKey("devices.device_id"), unique=True
    )  # Ensures one-to-one relation
    temp = Column(Float)
    soil_hum = Column(Float)
    air_hum = Column(Float)
    light = Column(Float)
    device = relationship("Device", back_populates="historical_data")
    created_at = Column(DateTime, default=datetime.utcnow)