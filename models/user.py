from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base


class User(Base):
    __tablename__ = "users"
    user_login = Column(String, primary_key=True)
    devices = relationship("Device", back_populates="user")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
