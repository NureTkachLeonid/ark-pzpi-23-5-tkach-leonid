import requests
import random
import time
from config import Config

def generate_sensor_data(plant_id: int):

    return {
        "plant_id": plant_id,
        "soil_moisture": random.randint(30, 80),
        "temperature": round(random.uniform(15.0, 30.0), 1),
        "light_level": random.randint(100, 1000)
    }

def main():
    print(f"Starting IoT Client for Device ID: {Config.DEVICE_ID}")
    print(f"Server URL: {Config.SERVER_URL}")
    print(f"Send Interval: {Config.SEND_INTERVAL} seconds")

    while True:
        try:
            data = generate_sensor_data(Config.DEVICE_ID)
            

            url = f"{Config.SERVER_URL}/api/sensor/data"
            
            response = requests.post(url, json=data)
            
            if response.status_code == 200:
                print(f"Data sent: {data}, Status: {response.status_code}")
            else:
                print(f"Failed to send data. Status: {response.status_code}, Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to server. Is the backend running?")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            
        time.sleep(Config.SEND_INTERVAL)

if __name__ == "__main__":
    main()
