from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

# Get DB URL from environment variable (Docker) or use default SQLite (Local)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

connect_args = {}
# SQLite requires this for multithreading, Postgres does not
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
