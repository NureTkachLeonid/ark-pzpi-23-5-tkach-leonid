from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    plants = relationship("Plant", back_populates="owner")

class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    species = Column(String)
    photo_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="plants")
    settings = relationship("PlantSettings", uselist=False, back_populates="plant")
    sensor_data = relationship("SensorData", back_populates="plant")

class PlantSettings(Base):
    __tablename__ = "plant_settings"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"), unique=True)
    min_moisture = Column(Integer, default=30)
    max_moisture = Column(Integer, default=80)
    min_temperature = Column(Float, default=15.0)
    max_temperature = Column(Float, default=30.0)
    min_light_level = Column(Integer, default=200)
    updated_at = Column(DateTime, default=datetime.utcnow)

    plant = relationship("Plant", back_populates="settings")

class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(Integer, ForeignKey("plants.id"))
    soil_moisture = Column(Integer)
    temperature = Column(Float)
    light_level = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    plant = relationship("Plant", back_populates="sensor_data")
