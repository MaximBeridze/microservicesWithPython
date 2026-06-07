# Application layer — Pydantic DTOs (Data Transfer Objects).
#
# This file defines the shapes of data coming IN and going OUT of the API.
# It is separate from models.py on purpose: the API shape is not always
# the same as the database shape (e.g. password comes in, never goes out).
#
# This file should define:
# - UserCreate  — fields accepted when creating a user (includes plain password)
# - UserOut     — fields returned to the caller (no password, ever)
# - UserList    — paginated envelope: { items, total, limit, offset }
#
# Use model_config = {"from_attributes": True} on UserOut so Pydantic can
# read directly from SQLAlchemy ORM objects.
#
# See the README for the full implementation.

from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str          # plain-text on the way in — hash it in the service layer

class UserOut(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class UserList(BaseModel):
    """Paginated envelope — all list endpoints return this shape."""
    items: list[UserOut]
    total: int
    limit: int
    offset: int