from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List
import database, models, services

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"]
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/backup")
def backup_database():
    """
    Адміністративна функція: Створити резервну копію бази даних.
    """
    return services.create_database_backup()


@router.get("/export/sensor-data")
def export_data(db: Session = Depends(get_db)):
    """
    Експорт всіх даних сенсорів у CSV форматі.
    """
    csv_data = services.export_sensor_data_csv(db)
    return Response(content=csv_data, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=sensor_data.csv"})


@router.post("/import/sensor-data")
async def import_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Імпорт даних з CSV файлу в базу даних.
    """
    content = await file.read()
    decoded_content = content.decode("utf-8")
    result = services.import_sensor_data_csv(db, decoded_content)
    return result


@router.patch("/users/{user_id}/block")
def block_user(user_id: int, is_active: bool, db: Session = Depends(get_db)):
    """
    Блокування/Розблокування користувача.
    """
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = is_active
    db.commit()
    return {"user_id": user_id, "is_active": user.is_active, "status": "Updated"}
