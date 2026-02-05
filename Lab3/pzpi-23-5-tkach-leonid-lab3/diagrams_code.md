# Mermaid Code for Lab 3 Diagrams

Copy and paste the code blocks below into a Mermaid Live Editor (e.g., https://mermaid.live/) to generate the images for your report.

## 1. Activity Diagram (Business Logic: Health Index Calculation)
This diagram shows the algorithm used in `services.calculate_plant_health_index`.

```mermaid
flowchart TD
    start([start])
    A["User/Client requests Analytics"]
    B["Server calls calculate_plant_health_index(plant_id, days)"]
    C["Fetch PlantSettings (min/max thresholds)"]
    D{"Settings found?"}
    E["Return Error Settings missing"]
    F([stop])
    G["Calculate start_date (Now - days)"]
    H["Fetch SensorData from DB (timestamp >= start_date)"]
    I{"Readings exist?"}
    J["Return Health Index = 0"]
    K["Initialize total_points = count(Readings)"]
    L["Initialize good_points = 0"]
    M{"Has more readings?"}
    N["Get next reading (moisture, temp)"]
    O{"Moisture in valid range?"}
    P["is_moisture_good = True"]
    Q["is_moisture_good = False"]
    R{"Temp in valid range?"}
    S["is_temp_good = True"]
    T["is_temp_good = False"]
    U{"is_moisture_good AND is_temp_good"}
    V["good_points += 1"]
    W{"is_moisture_good OR is_temp_good"}
    X["good_points += 0.5"]
    Y["good_points unchanged"]
    Z["Calculate Score = (good_points / total_points) * 100"]
    AA{"Score >= 90"}
    AB["Status = Perfect"]
    AC{"Score >= 75"}
    AD["Status = Good"]
    AE{"Score >= 50"}
    AF["Status = Needs Attention"]
    AG["Status = Critical"]
    AH["Return Result JSON"]
    AI([stop])
    
    start --> A
    A --> B
    B --> C
    C --> D
    D -->|No| E
    E --> F
    D -->|Yes| G
    G --> H
    H --> I
    I -->|No| J
    J --> F
    I -->|Yes| K
    K --> L
    L --> M
    M -->|Yes| N
    N --> O
    O -->|Yes| P
    O -->|No| Q
    P --> R
    Q --> R
    R -->|Yes| S
    R -->|No| T
    S --> U
    T --> U
    U -->|Yes| V
    U -->|No| W
    V --> M
    W -->|Yes| X
    W -->|No| Y
    X --> M
    Y --> M
    M -->|No| Z
    Z --> AA
    AA -->|Yes| AB
    AA -->|No| AC
    AB --> AH
    AC -->|Yes| AD
    AC -->|No| AE
    AD --> AH
    AE -->|Yes| AF
    AE -->|No| AG
    AF --> AH
    AG --> AH
    AH --> AI
```

## 2. Sequence Diagram (Admin Function: Backup)
This diagram shows the interaction for the Administrative Backup feature.

```mermaid
sequenceDiagram
    actor Admin
    participant "API Router\n(admin.py)" as API
    participant "Service Layer\n(services.py)" as Service
    participant "File System" as FS
    participant Database as DB

    Admin->>API: POST /api/admin/backup
    activate API
    API->>Service: create_database_backup()
    activate Service
    
    Service->>FS: Check if 'backups/' dir exists
    alt Dir missing
        Service->>FS: os.makedirs("backups")
    end
    
    Service->>FS: Define filename (backup_YYYY_MM_DD...)
    
    Service->>FS: shutil.copy2("sql_app.db", destination)
    activate FS
    FS-->>Service: File Copied
    deactivate FS
    
    Service-->>API: Return {"status": "success", "file": ...}
    deactivate Service
    
    API-->>Admin: 200 OK (Backup Created)
    deactivate API
```
