# Infrastructure layer — raw database queries.
#
# Functions here take a SQLAlchemy Session and return ORM objects.
# This is the only layer allowed to write SQL / ORM queries.
#
# Rules:
# - No HTTP knowledge here (no Request, no HTTPException)
# - No business rules here (no password hashing, no validation logic)
# - Every function receives `db: Session` as its first argument
#
# This file should implement:
# - create_user(db, data, hashed_password) -> User
# - get_user(db, user_id) -> User | None
# - list_users(db, limit, offset) -> tuple[list[User], int]
#
# See the README for the full implementation.

from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate

def create_user(db: Session, data: UserCreate, hashed_password: str) -> User:
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hashed_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def list_users(db: Session, limit: int = 20, offset: int = 0) -> tuple[list[User], int]:
    total = db.query(User).count()
    users = db.query(User).offset(offset).limit(limit).all()
    return users, total