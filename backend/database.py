"""
database.py
SQLAlchemy engine, session, and base setup for PostgreSQL.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv(Path(__file__).parent / ".env")
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency-style generator for FastAPI to get a DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()