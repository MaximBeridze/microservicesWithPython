# Infrastructure layer — ORM model.
#
# This is the only file that defines the shape of the `users` table.
# It maps Python attributes to database columns using SQLAlchemy.
#
# This file should:
# - Import Base from app.database
# - Define a User class with columns: id, username, email,
#   hashed_password, is_active, created_at
#
# Rule: no business logic here. This file only describes data structure.
#
# See the README for the full implementation.

from sqlalchemy import Column, String, Boolean, DateTime
from datetime import datetime, timezone
import uuid
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
