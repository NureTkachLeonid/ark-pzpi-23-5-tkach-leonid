from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from datetime import datetime, timedelta
import random

models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

def seed_data():

    user = db.query(models.User).filter(models.User.email == "demo@example.com").first()
    if not user:
        print("Creating demo user...")
        user = models.User(
            email="demo@example.com",
            password_hash="hashed_secret",
            full_name="Demo User",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        print("Demo user exists.")


    plant = db.query(models.Plant).filter(models.Plant.user_id == user.user_id).first()
    if not plant:
        print("Creating demo plant...")
        plant = models.Plant(
            user_id=user.user_id,
            name="Monstera Deliciosa",
            species="Monstera",
            photo_url="http://example.com/photo.jpg"
        )
        db.add(plant)
        db.commit()
        db.refresh(plant)
        

        settings = models.PlantSettings(
            plant_id=plant.plant_id,
            min_moisture=30, max_moisture=80,
            min_temperature=18.0, max_temperature=28.0,
            min_light_level=300
        )
        db.add(settings)
        db.commit()
    else:
        print("Demo plant exists.")


    data_count = db.query(models.SensorData).filter(models.SensorData.plant_id == plant.plant_id).count()
    if data_count < 20:
        print(f"Seeding sensor data (current count: {data_count})...")

        base_time = datetime.utcnow() - timedelta(days=7)
        for i in range(50): # 50 data points
            timestamp = base_time + timedelta(hours=i*3)
            

            mois = random.randint(40, 70)
            temp = random.uniform(20.0, 26.0)
            light = random.randint(300, 800)
            

            if i % 10 == 0:
                mois = 10
            
            reading = models.SensorData(
                plant_id=plant.plant_id,
                soil_moisture=mois,
                temperature=temp,
                light_level=light,
                timestamp=timestamp
            )
            db.add(reading)
        db.commit()
        print("Sensor data seeded.")
    else:
        print(f"Sufficient sensor data exists ({data_count} records).")

    db.close()

if __name__ == "__main__":
    seed_data()
