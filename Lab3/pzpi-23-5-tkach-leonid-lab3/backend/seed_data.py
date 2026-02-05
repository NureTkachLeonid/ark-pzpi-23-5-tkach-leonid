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
    
    # Always regenerate data for demo to ensure fresh "physics" logic
    print(f"Clearing old sensor data ({data_count} records)...")
    db.query(models.SensorData).filter(models.SensorData.plant_id == plant.plant_id).delete()
    db.commit()

    print("Seeding realistic sensor data...")
    base_time = datetime.utcnow() - timedelta(days=7)
    
    current_moisture = 75.0  # Start with watered plant
    
    for i in range(50): 
        timestamp = base_time + timedelta(hours=i*3)
        
        # Logic: moisture drops by 1-4% every 3 hours
        # If it drops below 35%, we "water" it (return to ~85%)
        current_moisture -= random.uniform(1.0, 4.0)
        if current_moisture < 35:
                current_moisture = 85.0
        
        # Simulate diurnal cycle for temp/light
        temp = random.uniform(20.0, 26.0)
        light = random.randint(300, 800)
        
        # Create an anomaly at the end for demo
        final_moisture = current_moisture
        if i == 45: 
            final_moisture = 15 

        reading = models.SensorData(
            plant_id=plant.plant_id,
            soil_moisture=int(final_moisture),
            temperature=temp,
            light_level=light,
            timestamp=timestamp
        )
        db.add(reading)
    db.commit()
    print("Realistic sensor data seeded.")

    db.close()

if __name__ == "__main__":
    seed_data()
