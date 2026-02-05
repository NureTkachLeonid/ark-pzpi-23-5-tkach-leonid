#!/bin/bash
set -e
export PATH=$PATH:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin:/Applications/Docker.app/Contents/Resources/bin

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed or not in PATH."
    echo "Please install Docker Desktop: https://docs.docker.com/get-started"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "Error: Docker daemon is not running."
    echo "Please start Docker Desktop application."
    exit 1
fi

DEFAULT_DB_USER="postgres"
DEFAULT_DB_PASSWORD="password"
DEFAULT_DB_NAME="smart_plants"
DEFAULT_DB_PORT="5432"
DEFAULT_SERVER_PORT="8000"

echo "=== Smart Plant System Setup ==="
echo "Generating .env file..."


read -p "Enter Database User [${DEFAULT_DB_USER}]: " DB_USER
DB_USER=${DB_USER:-$DEFAULT_DB_USER}

read -p "Enter Database Password [${DEFAULT_DB_PASSWORD}]: " DB_PASSWORD
DB_PASSWORD=${DB_PASSWORD:-$DEFAULT_DB_PASSWORD}

read -p "Enter Database Name [${DEFAULT_DB_NAME}]: " DB_NAME
DB_NAME=${DB_NAME:-$DEFAULT_DB_NAME}

read -p "Enter Database Port [${DEFAULT_DB_PORT}]: " DB_PORT
DB_PORT=${DB_PORT:-$DEFAULT_DB_PORT}

read -p "Enter Server Port [${DEFAULT_SERVER_PORT}]: " SERVER_PORT
SERVER_PORT=${SERVER_PORT:-$DEFAULT_SERVER_PORT}


cat > .env <<EOL
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_NAME=${DB_NAME}
DB_PORT=${DB_PORT}
SERVER_PORT=${SERVER_PORT}
EOL

echo ".env file created successfully."
echo "--------------------------------"
echo "Starting Docker Compose..."


if command -v docker-compose &> /dev/null
then
    docker-compose up --build -d
else

    docker compose up --build -d
fi

echo "--------------------------------"
echo "Containers started!"
echo "Backend API: http://localhost:${SERVER_PORT}/docs"
echo "Database: localhost:${DB_PORT}"
