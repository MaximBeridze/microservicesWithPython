# Infrastructure layer — database connection.
#
# Replicate the same structure as user-service/app/database.py.
# The only difference: the default DATABASE_URL points to games.db.
#
# This file should provide:
# - engine         — SQLAlchemy engine built from DATABASE_URL
# - SessionLocal   — session factory bound to the engine
# - Base           — DeclarativeBase that all ORM models inherit from
# - get_db()       — FastAPI dependency: yields a session, closes it after the request

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./games.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()