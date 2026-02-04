from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import models, schemas, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Smart Plant Care API",
    description="Backend API for IoT Plant Care System (Lab 2)",
    version="1.0.0"
)

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