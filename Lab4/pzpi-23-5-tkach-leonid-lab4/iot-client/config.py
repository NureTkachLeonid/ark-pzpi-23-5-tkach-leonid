import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SERVER_URL = os.getenv("SERVER_URL", "http://backend:8000")
    DEVICE_ID = int(os.getenv("DEVICE_ID", "1"))
    SEND_INTERVAL = int(os.getenv("SEND_INTERVAL", "5"))
