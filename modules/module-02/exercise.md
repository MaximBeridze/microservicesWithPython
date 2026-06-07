# Module 2 — FastAPI Service Design

**Duration**: 2h in class
**Branch to submit**: `module-02/<team-name>`

---

## Objective

You will build two services: explore the fully-built `user-service` as a reference, then build `game-service` yourself using the same structure. By the end of this module, both services run locally and respond to requests.

The architecture separates concerns into four layers:
- **models** — SQLAlchemy ORM model (what the DB table looks like)
- **schemas** — Pydantic DTOs (what the API sends and receives)
- **repository** — raw DB queries, no business logic
- **service** — business logic, calls the repository
- **routes** — HTTP layer, calls the service

---

## What's provided

`user-service` is fully implemented and documented. Read it before building anything — every file is annotated to explain its role and what belongs there.

Start it with:
```bash
cd services/user-service
cp .env.example .env
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8001
```

Open http://localhost:8001/docs and try the endpoints before writing any code.

The full file-by-file breakdown of `user-service` is in `services/user-service/README.md`. Read it — it explains what each file does and why.

---

## Required folder structure

Both `user-service` and `game-service` follow the same layout:

```
<service-name>/
├── app/
│   ├── __init__.py        # empty, makes app a package
│   ├── main.py            # FastAPI app init, mounts the router
│   ├── database.py        # engine + session factory
│   ├── models.py          # SQLAlchemy ORM model
│   ├── schemas.py         # Pydantic DTOs (input / output shapes)
│   ├── repository.py      # raw DB queries — no business logic here
│   ├── service.py         # business logic — calls repository
│   └── routes.py          # FastAPI router + endpoint handlers
├── alembic/
│   └── versions/          # auto-generated migration files go here
├── tests/
│   └── test_<name>.py
├── alembic.ini
├── requirements.txt
└── .env.example
```

See `services/user-service/README.md` for a file-by-file breakdown of what goes in each file — that is the working reference implementation.

---

## What you need to build

### game-service

Create `services/game-service/` using the structure above.

Your service must expose these four endpoints:

| Method | Path | Description |
|---|---|---|
| POST | `/v1/games` | Add a game to the catalogue |
| GET | `/v1/games` | List all games |
| GET | `/v1/games/{id}` | Get a game by ID |
| GET | `/v1/games/search?q=<term>` | Search games by name |

**A `Game` has at minimum**: `id`, `title`, `genre`, `platform`, `cover_url`.

For the search endpoint, use SQLAlchemy's `ilike` operator — it does a case-insensitive partial match.

Run it on port 8002:
```bash
cd services/game-service
cp .env.example .env
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8002
```

---

## Verify both services are running

```bash
curl http://localhost:8001/v1/users
curl http://localhost:8002/v1/games
```

Both should return a valid JSON response (empty list is fine).

Run the tests:
```bash
cd services/user-service && pytest tests/ -v
cd services/game-service && pytest tests/ -v
```

Check linting before you push — CI enforces both of these:
```bash
cd services/game-service
ruff check app/
mypy app/ --ignore-missing-imports
```

Also confirm `aiosqlite` is in your `requirements.txt` — the CI test runner uses a SQLite URL that requires it.

---

## Minimum to submit this branch

- [x] `game-service` running on port 8002 with all 4 endpoints working
- [x] Alembic migration for the `games` table committed
- [ ] At least one test passing in `game-service/tests/`
- [ ] `REFLECTION.md` completed and committed

If you run out of time: the search endpoint is optional. The other three are not.
