import shutil
import csv
import io
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import models

# --- BUSINESS LOGIC LAYER ---

def calculate_plant_health_index(db: Session, plant_id: int, period_days: int = 7) -> dict:
    """
    Business Logic: Calculates a 'Health Index' (0-100%) for a plant.
    Algorithm:
    1. Retrieve sensor data for the last N days.
    2. Retrieve plant settings (min/max thresholds).
    3. For each data point, check if it falls within the ideal range.
    4. Health Score = (Good Readings / Total Readings) * 100.
    """
    settings = db.query(models.PlantSettings).filter(models.PlantSettings.plant_id == plant_id).first()
    if not settings:
        return {"error": "Plant settings not found"}

    start_date = datetime.utcnow() - timedelta(days=period_days)
    readings = db.query(models.SensorData).filter(
        models.SensorData.plant_id == plant_id,
        models.SensorData.timestamp >= start_date
    ).all()

    if not readings:
        return {"health_index": 0, "status": "No Data", "period_days": period_days}

    total_points = len(readings)
    good_points = 0

    for r in readings:
        # Check moisture
        is_moisture_good = settings.min_moisture <= r.soil_moisture <= settings.max_moisture
        # Check temperature
        is_temp_good = settings.min_temperature <= r.temperature <= settings.max_temperature
        
        # Weighted score: Moisture is critical (60%), Temp is secondary (40%)
        # Here we simplistically count "perfect" readings where both are good
        if is_moisture_good and is_temp_good:
            good_points += 1
        elif is_moisture_good or is_temp_good:
             good_points += 0.5 # Partial credit

    score = round((good_points / total_points) * 100, 2)

    status = "Critical"
    if score >= 90:
        status = "Perfect"
    elif score >= 75:
        status = "Good"
    elif score >= 50:
        status = "Needs Attention"

    return {
        "plant_id": plant_id,
        "health_index": score,
        "status": status,
        "period_days": period_days,
        "total_readings": total_points
    }

# --- ADMIN SERVICES ---

def create_database_backup():
    """
    Creates a copy of the SQLite database file with a timestamp.
    """
    source = "sql_app.db"
    timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    destination = f"backups/backup_{timestamp}.db"
    
    # Ensure backups directory exists
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
    
    # Header
    writer.writerow(["sensor_data_id", "plant_id", "soil_moisture", "temperature", "light_level", "timestamp"])
    
    # Rows
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
        # Basic validation can be added here
        try:
            sensor_data = models.SensorData(
                plant_id=int(row["plant_id"]),
                soil_moisture=int(row["soil_moisture"]),
                temperature=float(row["temperature"]),
                light_level=int(row["light_level"]),
                # Timestamp parsing might be needed if provided, else default
            )
            db.add(sensor_data)
            count += 1
        except Exception:
            continue # Skip bad rows
            
    db.commit()
    return {"status": "success", "imported_rows": count}
