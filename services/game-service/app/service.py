# Application layer — business logic.
#
# Calls repository functions and returns Pydantic schemas (not raw ORM objects).
# Raises ValueError when a game is not found — routes.py turns it into a 404.
#
# Implement these four functions:
# - add_game(db, data) -> GameOut
# - fetch_game(db, game_id) -> GameOut        (raises ValueError if not found)
# - fetch_all_games(db, limit, offset) -> GameList
# - find_games(db, q, limit, offset) -> GameList   (delegates to search_games in repository)
#
# Module 5 — CQRS:
# In add_game(), after saving to the DB, also write to the Redis cache:
#   from app.infrastructure.cache import set_game_summary
#   set_game_summary(game.id, {"id": game.id, "title": game.title,
#                               "genre": game.genre, "platform": game.platform,
#                               "cover_url": game.cover_url})

from sqlalchemy.orm import Session
from app import repository
from app.schemas import GameCreate, GameOut, GameList

def add_game(db: Session, data: GameCreate) -> GameOut:
    game = repository.create_game(db, data)
    return GameOut.model_validate(game)

def fetch_game(db: Session, game_id: str) -> GameOut:
    game = repository.get_game(db, game_id)
    if game is None:
        raise ValueError(f"Game {game_id} not found")
    return GameOut.model_validate(game)

def fetch_all_games(db: Session, limit: int = 20, offset: int = 0) -> GameList:
    games, total = repository.list_games(db, limit=limit, offset=offset)
    return GameList(
        items=[GameOut.model_validate(game) for game in games],
        total=total,
        limit=limit,
        offset=offset,
    )

def find_games(db: Session, q: str, limit: int = 20, offset: int = 0) -> GameList:
    games, total = repository.search_games(db, q=q, limit=limit, offset=offset)
    return GameList(
        items=[GameOut.model_validate(game) for game in games],
        total=total,
        limit=limit,
        offset=offset,
    )