from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- Sensor Data Schemas ---
# Ця схема використовується для прийому даних від IoT пристрою (C++)
class SensorDataCreate(BaseModel):
    plant_id: int
    soil_moisture: int
    temperature: float
    light_level: int
    
    class Config:
        from_attributes = True

class SensorDataResponse(SensorDataCreate):
    id: int
    timestamp: datetime

# --- Plant Schemas ---
class PlantBase(BaseModel):
    name: str
    species: str
    photo_url: Optional[str] = None

class PlantCreate(PlantBase):
    user_id: int # Тимчасово передаємо явно

class PlantResponse(PlantBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
