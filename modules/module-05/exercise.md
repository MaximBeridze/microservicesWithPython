# Module 5 — Data Management & CQRS

**Duration**: 2h in class
**Branch to submit**: `module-05/<team-name>`

---

## Objective

Not all data is the same. Some data needs to be written once and read accurately (a user's account). Other data needs to be read thousands of times per second and can tolerate being slightly stale (a game's summary).

This module introduces two ideas: **CQRS** (separating read and write models) and the **GDPR consent lifecycle** (which forces you to think about what you are even allowed to store).

---

## Before you start

Your module-04 work must be in place: gateway on port 8000, RabbitMQ running, activity-service publishing messages.

Start Redis:

```bash
docker compose -f docker-compose.infra.yml up -d redis
```

Confirm it's up:

```bash
docker compose -f docker-compose.infra.yml ps
```

---

## What's provided

- The `game-service` CQRS scaffolding is in place: SQLite is the write model, Redis is the read model. The cache write logic is implemented in `game-service/app/infrastructure/cache.py` — you wire up the read side.
- The `logging-service` skeleton is provided (Flask, not FastAPI — intentional). The RabbitMQ consumer is scaffolded. You implement the consent endpoints.
- `logging-service` uses Flask: routes are `@app.route(...)`, no Pydantic, run with `flask run --port 8006`.

Install new dependencies:

```bash
cd services/game-service && pip install -r requirements.txt
cd services/logging-service && pip install -r requirements.txt
```

---

## Part A — CQRS in game-service *(~40 min)*

When a game is added, it writes to two places:
- **SQLite** — the authoritative write model
- **Redis** — a denormalised projection for fast reads

Two endpoints serve the same game differently:
- `GET /v1/games/{id}` — reads from SQLite (full, accurate data)
- `GET /v1/games/{id}/summary` — reads from Redis (fast, potentially stale)

Your task: wire up the `/summary` endpoint to read from Redis. The cache key format and the write side are already implemented in `game-service/app/infrastructure/cache.py` — follow the same pattern for the read.

Test the difference by adding a game through the gateway, then calling both endpoints. Confirm the summary returns data from Redis.

---

## Part B — GDPR consent lifecycle in logging-service *(~45 min)*

The `logging-service` consumes activity events from RabbitMQ (the same broker you set up in module-04). Before writing any log entry, it must check that the user has given consent.

Implement the four consent endpoints in `logging-service/app/main.py`:

| Method | Path | Description |
|---|---|---|
| POST | `/v1/consent/{user_id}` | User opts in to activity logging |
| GET | `/v1/consent/{user_id}` | Check consent status |
| DELETE | `/v1/consent/{user_id}` | User withdraws consent |
| DELETE | `/v1/logs/{user_id}` | GDPR right to erasure — delete all logs for this user |

The RabbitMQ consumer already calls `has_consent(user_id)` before writing — implement that function in the consent model.

Register `logging-service` in the gateway. Open `gateway/app/config.py` and `gateway/app/main.py` — the lines for `logging-service` are already there, commented out with `# Added in Module 5`. Uncomment them. Note that two route entries point to the same service:

```python
"consent": settings.logging_service_url,
"logs":    settings.logging_service_url,
```

Test the full flow in order:

1. Start logging-service: `flask run --port 8006`
2. `GET /v1/consent/{user_id}` — confirm no consent on record
3. Log an activity — confirm no log is written (no consent yet)
4. `POST /v1/consent/{user_id}` — opt in
5. Log another activity — confirm the log appears via `GET /v1/logs/{user_id}`
6. `DELETE /v1/consent/{user_id}` — withdraw consent
7. `DELETE /v1/logs/{user_id}` — erase all logs for that user

---

## Discussion *(~15 min)*

- You now have two models for a game's data. What happens if a game's title is updated in SQLite but the Redis projection is not refreshed? Who notices first — the developer or the user?
- The GDPR consent check is inside `logging-service`, not at the gateway. Why there and not earlier in the chain?
- With CQRS, your write model and read model can drift. In what scenario does that inconsistency matter to the user? In what scenario is it completely acceptable?

---

## Minimum to submit this branch

- [ ] `GET /v1/games/{id}/summary` returns data from Redis
- [ ] All four consent endpoints working and reachable via the gateway
- [ ] RabbitMQ consumer skips log entries when consent is not given
- [ ] `logging-service` registered in the gateway under both `consent` and `logs`
- [ ] `REFLECTION.md` completed and committed

---

> **Needs to be built before this module runs:**
> - `services/game-service/app/infrastructure/cache.py` — Redis cache read/write scaffolding (write side implemented, `/summary` read side left as TODO)
> - `services/logging-service/` — Flask skeleton with RabbitMQ consumer scaffolded and consent model stubbed out; students implement the four endpoints
