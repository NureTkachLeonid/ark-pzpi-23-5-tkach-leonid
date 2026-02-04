-- Database Schema for Smart Plant Care System
-- Author: Leonid Tkach (PZPI-23-5)

-- Create Users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Plants table
CREATE TABLE plants (
    plant_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    species VARCHAR(100),
    photo_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Create Plant Settings table (One-to-One relationship with Plants usually, or One-to-Many)
CREATE TABLE plant_settings (
    setting_id SERIAL PRIMARY KEY,
    plant_id INT NOT NULL,
    min_moisture INT DEFAULT 30,
    max_moisture INT DEFAULT 80,
    min_temperature FLOAT DEFAULT 15.0,
    max_temperature FLOAT DEFAULT 30.0,
    min_light_level INT DEFAULT 200,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_plant_settings FOREIGN KEY (plant_id) REFERENCES plants(plant_id) ON DELETE CASCADE
);

-- Create Sensor Data table (TimeSeries data)
CREATE TABLE sensor_data (
    sensor_data_id SERIAL PRIMARY KEY,
    plant_id INT NOT NULL,
    soil_moisture INT NOT NULL,
    temperature FLOAT,
    light_level INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_plant_data FOREIGN KEY (plant_id) REFERENCES plants(plant_id) ON DELETE CASCADE
);

-- Indexes for performance optimization
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_plants_user_id ON plants(user_id);
CREATE INDEX idx_sensor_data_plant_id_timestamp ON sensor_data(plant_id, timestamp DESC);
