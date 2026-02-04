from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SensorDataCreate(BaseModel):
    plant_id: int
    soil_moisture: int
    temperature: float
    light_level: int
    
    class Config:
        from_attributes = True

class SensorDataResponse(SensorDataCreate):
    sensor_data_id: int
    timestamp: datetime

class PlantBase(BaseModel):
    name: str
    species: str
    photo_url: Optional[str] = None

class PlantCreate(PlantBase):
    user_id: int 

class PlantResponse(PlantBase):
    plant_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PlantSettingsBase(BaseModel):
    min_moisture: int = 30
    max_moisture: int = 80
    min_temperature: float = 15.0
    max_temperature: float = 30.0
    min_light_level: int = 200

class PlantSettingsUpdate(PlantSettingsBase):
    pass

class PlantSettingsResponse(PlantSettingsBase):
    setting_id: int
    plant_id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True
