from sqlalchemy import Column, Integer, ForeignKey, Float, Date, String
from datetime import date
from models.base import Base


class DailyAverages(Base):
    __tablename__ = "daily_averages"
    daily_averages_id = Column(Integer, primary_key=True)
    device_id = Column(String, ForeignKey("devices.device_id"))
    avg_temp = Column(Float)
    avg_soil_hum = Column(Float)
    avg_air_hum = Column(Float)
    avg_light = Column(Float)
    date = Column(Date, default=date.today)
