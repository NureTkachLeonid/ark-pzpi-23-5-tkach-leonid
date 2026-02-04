# Інструкція зі створення діаграм для Smart Plant Care (Lab 2)

Вам потрібно створити 3 діаграми у Draw.io, аналогічні до тих, що у Грега, але для вашої теми (Рослини).

## 1. UML Діаграма прецедентів (Use Case) - Як Рисунок 1
**Актори:**
- **User (Користувач)** - зліва.
- **IoT Device (Сенсор/ESP32)** - справа (або теж зліва, як зручно).

**Овали (Use Cases) посередині:**
1. **Реєстрація/Вхід** (User)
2. **Перегляд списку рослин** (User)
3. **Додавання нової рослини** (User) -> *include* -> **Налаштування меж поливу**
4. **Перегляд графіків (вологість/температура)** (User)
5. **Отримання Push-сповіщення** (User)
6. **Відправка даних телеметрії** (IoT Device) -> *стрілка до системи*
7. **Автоматична перевірка показників** (System/Timer)

*Стрілки:* Від User до oval'ів. Від IoT Device до "Відправка даних".

## 2. Діаграма класів (Class Diagram) - Як Рисунок 2
Цей варіант ідеально підходить. Ви можете намалювати його вручну блоками або вставити цей код у Draw.io (Arrange -> Insert -> Advanced -> Mermaid).

```mermaid
classDiagram
    %% --- API LAYER (Controllers) ---
    class AuthController {
        +register(user: UserCreate)
        +login(credentials: UserLogin)
    }

    class PlantController {
        +create_plant(plant: PlantCreate)
        +get_plant(id: int)
        +update_plant(id: int, data: PlantUpdate)
        +delete_plant(id: int)
        +update_settings(id: int, settings: SettingsUpdate)
    }

    class SensorDataController {
        +receive_telemetry(data: SensorDataInput)
        +get_stats(plant_id: int, period: string)
    }

    class AdminController {
        +get_all_users()
        +generate_daily_report()
    }

    %% --- SERVICE LAYER (Business Logic) ---
    class AuthService {
        +verify_password(plain: str, hashed: str)
        +get_password_hash(password: str)
        +create_access_token(data: dict)
    }

    class SensorDataService {
        +validate_sensor_data(data: SensorDataInput)
        +save_to_db(data: SensorDataInput)
        +check_thresholds(plant_id: int, current_data: SensorDataInput)
    }

    class NotificationSystem {
        +send_alert(user_id: int, message: string)
    }

    %% --- DATA LAYER (Models / Entities) ---
    class User {
        +int id
        +string email
        +string full_name
        +string password_hash
        +datetime created_at
    }

    class Plant {
        +int id
        +int user_id
        +string name
        +string species
        +string photo_url
    }

    class PlantSettings {
        +int id
        +int plant_id
        +int min_moisture
        +int max_moisture
        +float min_temp
        +float max_temp
    }

    class SensorData {
        +int id
        +int plant_id
        +int soil_moisture
        +float temperature
        +int light_level
        +datetime timestamp
    }

    %% --- RELATIONSHIPS ---
    %% Controllers use Services
    AuthController ..> AuthService : uses
    SensorDataController ..> SensorDataService : uses
    SensorDataService ..> NotificationSystem : triggers

    %% Models relationships
    User "1" *-- "0..*" Plant : owns
    Plant "1" *-- "1" PlantSettings : has
    Plant "1" *-- "0..*" SensorData : history

    %% Services manipulate Models
    SensorDataService ..> SensorData : creates
    SensorDataService ..> PlantSettings : reads
```

## 3. ER-діаграма (Схема БД) - Як Рисунок 3
Відображає таблиці та зв'язки (Crow's Foot notation - "лапка ворони").

**Сутності (Таблиці):**
1. **users**
   - PK: `id` (int)
   - `email` (varchar)
   - `password_hash` (varchar)
   
2. **plants**
   - PK: `id` (int)
   - FK: `user_id` (int) -> лінія до users
   - `name`, `species`

3. **plant_settings**
   - PK: `id` (int)
   - FK: `plant_id` (int) -> лінія до plants
   - `min_moisture`, `max_moisture`

4. **sensor_data**
   - PK: `id` (int)
   - FK: `plant_id` (int) -> лінія до plants
   - `soil_moisture`, `temperature`, `timestamp`

*Зв'язки:*
- users `||--o{` plants (Один до багатьох)
- plants `||--||` plant_settings (Один до одного)
- plants `||--o{` sensor_data (Один до багатьох)
