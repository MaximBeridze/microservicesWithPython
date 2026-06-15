# Module 5 — CQRS read model.
#
# SQLite is the write model (authoritative). Redis is the read model (fast, potentially stale).
#
# Write side (set_game_summary): IMPLEMENTED — call it from add_game() in service.py
#   after the game is saved to SQLite.
#
# Read side (get_game_summary): YOUR TASK — implement it, then add the
#   GET /v1/games/{game_id}/summary endpoint in routes.py that calls it.

import json
import os

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

_client: redis.Redis | None = None


def _get_client() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.from_url(REDIS_URL, decode_responses=True)
    return _client


def _key(game_id: str) -> str:
    return f"game:summary:{game_id}"


# ---------------------------------------------------------------------------
# Write side — implemented, call this from service.py after creating a game
# ---------------------------------------------------------------------------

def set_game_summary(game_id: str, data: dict) -> None:
    r = _get_client()
    r.set(_key(game_id), json.dumps(data))


# ---------------------------------------------------------------------------
# Read side — YOUR TASK
# ---------------------------------------------------------------------------

def get_game_summary(game_id: str) -> dict | None:
    r = _get_client()
    raw = r.get(_key(game_id))
    if raw is None:
        return None
    return json.loads(raw)
