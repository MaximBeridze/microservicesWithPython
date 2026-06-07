# Application layer — business logic.
#
# This is where decisions live: hashing passwords, raising errors when a user
# is not found, converting ORM objects into Pydantic schemas before returning.
#
# Rules:
# - Only calls repository functions — never queries the DB directly
# - Returns Pydantic schemas (UserOut, UserList), not raw ORM objects
# - Raises ValueError for business errors (routes.py turns them into HTTP errors)
#
# This file should implement:
# - add_user(db, data) -> UserOut
# - fetch_user(db, user_id) -> UserOut   (raises ValueError if not found)
# - fetch_all_users(db, limit, offset) -> UserList
#
# Note: _hash_password is a placeholder for now — it will be replaced
# with passlib in Module 6.
#
# See the README for the full implementation.

from sqlalchemy.orm import Session
from app import repository
from app.schemas import UserCreate, UserOut, UserList

def _hash_password(plain: str) -> str:
    # for now a placeholder — swap for passlib in Module 6
    return plain + "_hashed"

def add_user(db: Session, data: UserCreate) -> UserOut:
    hashed = _hash_password(data.password)
    user = repository.create_user(db, data, hashed)
    return UserOut.model_validate(user)

def fetch_user(db: Session, user_id: str) -> UserOut:
    user = repository.get_user(db, user_id)
    if user is None:
        raise ValueError(f"User {user_id} not found")
    return UserOut.model_validate(user)

def fetch_all_users(db: Session, limit: int = 20, offset: int = 0) -> UserList:
    users, total = repository.list_users(db, limit=limit, offset=offset)
    return UserList(
        items=[UserOut.model_validate(u) for u in users],
        total=total,
        limit=limit,
        offset=offset,
    )