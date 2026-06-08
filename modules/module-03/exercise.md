# Module 3 — Synchronous Communication

**Duration**: 2h in class
**Branch to submit**: `module-03/<team-name>`

---

## Objective

Services need to talk to each other. In this module you build the gateway that became the entry point on your Module 1 service map, then wire up `activity-service` to call `user-service` and `game-service` through it.

By the end of this module, all client requests go through port 8000. No client ever calls a service on its own port again.

---

## What's provided

The `activity-service` skeleton is already in place — models, schemas, and repository are done. Your job is to add the inter-service calls.

The gateway boilerplate (project structure, `config.py`, catch-all route skeleton) is in `modules/module-03/gateway-starter/`. Copy it to `gateway/` and fill in the missing logic.

---

## Part A — Build the gateway _(~40 min)_

The gateway has one job: read the URL path and forward the request to the right service. No auth, no business logic — just routing.

It uses a `ROUTES` dictionary:

```python
ROUTES = {
    "users":      "http://localhost:8001",
    "games":      "http://localhost:8002",
    "activities": "http://localhost:8003",
}
```

When a request arrives at `/v1/users/123`, the gateway splits the path, finds `users` in the dictionary, and forwards the full request to `http://localhost:8001/v1/users/123` — method, headers, and body preserved exactly.

Edge cases to handle:

- Unknown resource → `404`
- Downstream service unreachable → `503 Service Unavailable`
- `/health` → handled by the gateway itself, never forwarded

Once the gateway is implemented, start user-service, game-service, and the gateway, then verify the two existing services route correctly before moving on:

```bash
uvicorn app.main:app --reload --port 8000  # gateway
uvicorn app.main:app --reload --port 8001  # user-service
uvicorn app.main:app --reload --port 8002  # game-service
```

```bash
curl http://localhost:8000/health        # {"status": "ok"}
curl http://localhost:8000/v1/users      # proxied to user-service
curl http://localhost:8000/v1/games      # proxied to game-service
curl http://localhost:8000/v1/unknown    # 404
```

Only move to Part B once these pass.

---

## Part B — Wire up the activity-service _(~50 min)_

Every time an activity is created, the activity-service makes two outbound calls:

1. **Validate** that the user exists in `user-service` — if not, return `404`
2. **Enrich** the response with game data from `game-service` — if unreachable, return `"game": null`

These two calls are handled differently on purpose:

- Validation is **critical** — the request must not proceed if the user doesn't exist. It retries on transient errors.
- Enrichment is **optional** — the activity is saved regardless. It fails gracefully with a null fallback.

> **Why is there no `seed.py` for activity-service?**
> `user-service` and `game-service` each have a self-contained `seed.py` that inserts rows directly into their own database. That works because they own their data entirely.
> Activity-service can't do the same — it doesn't own user IDs or game IDs. A seed script for activities would have to call the APIs of both other services to fetch real UUIDs first, and only then POST to activity-service. It only works when the full stack is running.
> That dependency is not a problem to fix — it is the point. Each service owns its data, and that constraint has real operational consequences. You'll create activities live during this module as part of testing, which is exactly the right way to exercise the inter-service calls you're about to implement.

Open `services/activity-service/app/main.py` and implement both functions. The signatures and the expected response shape are documented in `docs/api-contracts.md`.

Once implemented, start activity-service and add it to the running stack:

```bash
uvicorn app.main:app --reload --port 8003  # activity-service
```

Test the full flow through the gateway:

```bash
# Create a user first, then log an activity for that user
curl -X POST http://localhost:8000/v1/activities -H "Content-Type: application/json" -d '{"user_id": "<your-user-id>", "game_id": "<your-game-id>", "action": "played"}'
```

Check that the response includes the enriched `game` object. Then stop `game-service` and repeat — confirm the activity is still saved with `"game": null`.

---

## Discussion _(~15 min)_

- The downstream services did not change at all when you added the gateway. What does that tell you about the pattern?
- Why does the validation call retry on failure but the enrichment call doesn't?
- What happens to the overall response time if `user-service` is slow?

---

## Minimum to submit this branch

- [x] `activity-service` validates users and enriches with game data
- [x] Graceful degradation works: activity saved even when `game-service` is down
- [x] Gateway running on port 8000, routing to all three services
- [x] `curl http://localhost:8000/health` returns `{"status": "ok"}`
- [x] `REFLECTION.md` completed and committed

---

## Optional — gRPC

If you finish early, read `modules/module-03/grpc-reading.md` for an introduction to gRPC as an alternative to REST for internal service calls. No implementation required.
