# Infrastructure layer — database connection.
#
# This file is responsible for:
# - Creating the SQLAlchemy engine from DATABASE_URL (read from .env)
# - Defining the declarative Base that all ORM models inherit from
# - Providing get_db(), a FastAPI dependency that opens a session per request
#   and closes it when the request is done (using yield)
#
# Nothing in this file knows about Users, Games, or any business concept.
# It is pure infrastructure.
#
# See the README for the full implementation.

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./users.db")

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