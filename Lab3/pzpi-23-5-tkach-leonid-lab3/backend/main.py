from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models, schemas, database, services, admin

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Smart Plant Care API",
    description="Backend API for IoT Plant Care System (Lab 2 + Lab 3)",
    version="1.1.0"
)

app.include_router(admin.router)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to Smart Plant Care API"}

@app.post("/api/sensor/data", response_model=schemas.SensorDataResponse, tags=["IoT"])
def receive_sensor_data(data: schemas.SensorDataCreate, db: Session = Depends(get_db)):
    """
    Прийом телеметрії від IoT-пристрою (ESP32).
    Зберігає вологість, температуру та освітлення в БД.
    """
    plant = db.query(models.Plant).filter(models.Plant.plant_id == data.plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    db_sensor_data = models.SensorData(
        plant_id=data.plant_id,
        soil_moisture=data.soil_moisture,
        temperature=data.temperature,
        light_level=data.light_level
    )
    db.add(db_sensor_data)
    db.commit()
    db.refresh(db_sensor_data)
    return db_sensor_data

@app.post("/api/plants", response_model=schemas.PlantResponse, tags=["Plants"])
def create_plant(plant: schemas.PlantCreate, db: Session = Depends(get_db)):
    db_plant = models.Plant(**plant.dict())
    db.add(db_plant)
    db.commit()
    db.refresh(db_plant)
    return db_plant

@app.get("/api/plants", response_model=List[schemas.PlantResponse], tags=["Plants"])
def read_plants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    plants = db.query(models.Plant).offset(skip).limit(limit).all()
    return plants

@app.get("/api/plants/{plant_id}/stats", response_model=List[schemas.SensorDataResponse], tags=["IoT"])
def read_sensor_stats(plant_id: int, db: Session = Depends(get_db)):
    """
    Отримати історію показників для конкретної рослини.
    """
    readings = db.query(models.SensorData).filter(models.SensorData.plant_id == plant_id).all()
    return readings

@app.get("/api/plants/{plant_id}/settings", response_model=schemas.PlantSettingsResponse, tags=["Settings"])
def read_plant_settings(plant_id: int, db: Session = Depends(get_db)):
    """
    Отримати поточні налаштування (межі поливу, температури) для рослини.
    Якщо налаштувань немає — створюються дефолтні.
    """
    settings = db.query(models.PlantSettings).filter(models.PlantSettings.plant_id == plant_id).first()
    if not settings:
        settings = models.PlantSettings(plant_id=plant_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@app.put("/api/plants/{plant_id}/settings", response_model=schemas.PlantSettingsResponse, tags=["Settings"])
def update_plant_settings(plant_id: int, settings: schemas.PlantSettingsUpdate, db: Session = Depends(get_db)):
    """
    Оновити налаштування (наприклад, встановити нову мін. вологість).
    """
    db_settings = db.query(models.PlantSettings).filter(models.PlantSettings.plant_id == plant_id).first()
    if not db_settings:
        db_settings = models.PlantSettings(plant_id=plant_id)
        db.add(db_settings)
    
    for var, value in settings.dict(exclude_unset=True).items():
        setattr(db_settings, var, value)
    
    db_settings.updated_at = datetime.utcnow()
    db.add(db_settings)
    db.commit()
    db.refresh(db_settings)
    return db_settings

# --- Business Logic Endpoint ---
# --- Business Logic & Analytics Endpoints ---

@app.get("/api/plants/{plant_id}/analytics/forecast", tags=["Analytics"])
def get_moisture_forecast(plant_id: int, db: Session = Depends(get_db)):
    """
    Прогноз вологості (EWMA) з кліматичною корекцією.
    """
    return services.forecast_moisture(db, plant_id)

@app.get("/api/plants/{plant_id}/analytics/stats", tags=["Analytics"])
def get_plant_stats(plant_id: int, db: Session = Depends(get_db)):
    """
    Середні показники за весь час.
    """
    return services.get_average_stats_per_plant(db, plant_id)

@app.get("/api/plants/{plant_id}/analytics/hourly", tags=["Analytics"])
def get_hourly_stats(plant_id: int, db: Session = Depends(get_db)):
    """
    Погодинна статистика температури (циркадні ритми).
    """
    return services.get_hourly_sensor_data(db, plant_id)