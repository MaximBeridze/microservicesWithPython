from collections.abc import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def create_game(client: TestClient, title: str = "Hades") -> dict:
    response = client.post(
        "/v1/games/",
        json={
            "title": title,
            "genre": "Roguelike",
            "platform": "PC",
            "release_year": 2020,
            "cover_url": "https://example.com/hades.jpg",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_game_returns_created_game(client: TestClient):
    data = create_game(client)

    assert data["id"]
    assert data["title"] == "Hades"
    assert data["genre"] == "Roguelike"
    assert data["platform"] == "PC"
    assert data["release_year"] == 2020
    assert data["cover_url"] == "https://example.com/hades.jpg"
    assert data["created_at"]


def test_get_game_by_id_returns_game(client: TestClient):
    created = create_game(client, title="Celeste")

    response = client.get(f"/v1/games/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["title"] == "Celeste"


def test_get_unknown_game_returns_404(client: TestClient):
    response = client.get("/v1/games/missing-game-id")

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_list_games_returns_paginated_envelope(client: TestClient):
    create_game(client, title="Hades")
    create_game(client, title="Celeste")

    response = client.get("/v1/games/")
    data = response.json()

    assert response.status_code == 200
    assert data["total"] == 2
    assert data["limit"] == 20
    assert data["offset"] == 0
    assert [game["title"] for game in data["items"]] == ["Hades", "Celeste"]


def test_search_games_returns_matching_titles_only(client: TestClient):
    create_game(client, title="Hades")
    create_game(client, title="Celeste")
    create_game(client, title="Halo Infinite")

    response = client.get("/v1/games/search", params={"q": "ha"})
    data = response.json()

    assert response.status_code == 200
    assert data["total"] == 2
    assert [game["title"] for game in data["items"]] == ["Hades", "Halo Infinite"]
