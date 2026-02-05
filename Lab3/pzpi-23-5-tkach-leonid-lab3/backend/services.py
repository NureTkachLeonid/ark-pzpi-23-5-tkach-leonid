import shutil
import csv
import io
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import models





def calculate_ewma(data: list[float], alpha: float) -> float:
    smoothed = data[0]
    for i in range(1, len(data)):
        smoothed = alpha * data[i] + (1 - alpha) * smoothed
    return smoothed

def get_optimal_alpha(data: list[float]) -> float:

    if not data:
        return 0.5
    avg = sum(data) / len(data)
    variance = sum((x - avg)**2 for x in data) / len(data)
    if variance > 50:
        return 0.4
    return 0.2

def weather_correction(base_forecast: float, temp: float) -> float:

    factor = 1.0
    if temp > 25.0:
        factor = 1.0 + 0.05 * (temp - 25.0)
    
    return base_forecast / factor

def forecast_moisture(db: Session, plant_id: int):

    readings = db.query(models.SensorData).filter(
        models.SensorData.plant_id == plant_id
    ).order_by(models.SensorData.timestamp.asc()).all()
    
    values = [float(d.soil_moisture) for d in readings]
    temps = [float(d.temperature) for d in readings]
    
    if len(values) < 2:
        return {"error": "Not enough data for forecast"}

    alpha = get_optimal_alpha(values)
    ewma_val = calculate_ewma(values, alpha)
    

    current_temp = temps[-1] if temps else 25.0
    corrected_forecast = weather_correction(ewma_val, current_temp)
    

    current = values[-1]
    trend = corrected_forecast - current
    
    return {
        "current_moisture": current,
        "forecast_ewma_corrected": round(corrected_forecast, 2),
        "trend": round(trend, 2),
        "alert": corrected_forecast < 30
    }

def get_average_stats_per_plant(db: Session, plant_id: int):
    stats = db.query(
        func.avg(models.SensorData.soil_moisture),
        func.avg(models.SensorData.temperature),
        func.avg(models.SensorData.light_level)
    ).filter(models.SensorData.plant_id == plant_id).first()
    
    return {
        "avg_moisture": round(stats[0] or 0, 1),
        "avg_temp": round(stats[1] or 0, 1),
        "avg_light": round(stats[2] or 0, 1)
    }

def get_hourly_sensor_data(db: Session, plant_id: int):

    results = db.query(
        func.strftime('%H', models.SensorData.timestamp).label('hour'),
        func.avg(models.SensorData.temperature)
    ).filter(models.SensorData.plant_id == plant_id)\
     .group_by('hour').all()
    
    return [{"hour": int(r.hour), "avg_temp": round(r[1], 1)} for r in results]


def calculate_plant_health_index(db: Session, plant_id: int, period_days: int = 7) -> dict:
    return get_average_stats_per_plant(db, plant_id)



def create_database_backup():
    """
    Creates a copy of the SQLite database file with a timestamp.
    """
    source = "sql_app.db"
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    destination = f"backups/backup_{timestamp}.db"
    

    import os
    if not os.path.exists("backups"):
        os.makedirs("backups")
        
    try:
        shutil.copy2(source, destination)
        return {"status": "success", "file": destination}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def export_sensor_data_csv(db: Session) -> str:
    """
    Exports all sensor data to a CSV string.
    """
    data = db.query(models.SensorData).all()
    output = io.StringIO()
    writer = csv.writer(output)
    

    writer.writerow(["sensor_data_id", "plant_id", "soil_moisture", "temperature", "light_level", "timestamp"])
    

    for row in data:
        writer.writerow([
            row.sensor_data_id, 
            row.plant_id, 
            row.soil_moisture, 
            row.temperature, 
            row.light_level, 
            row.timestamp
        ])
        
    return output.getvalue()

def import_sensor_data_csv(db: Session, csv_content: str):
    """
    Imports sensor data from a CSV string.
    """
    csv_file = io.StringIO(csv_content)
    reader = csv.DictReader(csv_file)
    
    count = 0
    for row in reader:

        try:
            sensor_data = models.SensorData(
                plant_id=int(row["plant_id"]),
                soil_moisture=int(row["soil_moisture"]),
                temperature=float(row["temperature"]),
                light_level=int(row["light_level"]),
            )
            db.add(sensor_data)
            count += 1
        except Exception:
            continue
            
    db.commit()
    return {"status": "success", "imported_rows": count}
