from sqlalchemy import Column, Integer, ForeignKey, Float, Date
from datetime import date
from models.base import Base


class DailyAverage(Base):
    __tablename__ = "daily_averages"
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.device_id"))
    avg_temp = Column(Float)
    avg_soil_hum = Column(Float)
    avg_air_hum = Column(Float)
    avg_light = Column(Float)
    date = Column(Date, default=date.today)
