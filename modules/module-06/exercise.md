# Module 6 — Security

**Duration**: 2h in class
**Branch to submit**: `module-06/<team-name>`

---

## Objective

Until now, the gateway forwarded every request blindly. Any client that knew the port could call any service. This module locks the front door: the gateway validates a JWT before forwarding anything, and services enforce roles on sensitive operations.

You will trace a token from the moment it is created to the moment it is rejected — and you will write the two functions that make that possible.

---

## Before you start

Your module-05 work must be in place: gateway on port 8000, Redis and RabbitMQ running.

```bash
docker compose -f docker-compose.infra.yml up -d redis rabbitmq
```

Install auth-service dependencies:

```bash
cd services/auth-service
pip install -r requirements.txt
```

---

## What's provided

The `auth-service` scaffold is in `services/auth-service/`. The project structure, config, user store, and both endpoints are already in place. Two things are left empty for you to implement:

- `app/security.py` — `create_access_token()` and `get_current_user()`

Everything else is wired up and ready. Once you implement those two functions, the service starts and issues real tokens.

Three users exist in the user store (`app/users.py`) — you do not need to add anything:
- `testuser` / `password` — role: `gamer`
- `admin` / `adminpass` — role: `admin`
- `activity-service` / `m2m-secret` — role: `service` (used for M2M calls)

---

## Part A — Build the two core functions *(~35 min)*

Open `services/auth-service/app/security.py`. You will find two empty functions with docstrings explaining exactly what each must do.

**`create_access_token(data: dict) -> str`**
Takes a dictionary of claims (e.g. `{"sub": "testuser", "role": "gamer"}`), adds an expiry timestamp (`exp`), and returns a signed JWT string. Use `python-jose` with `HS256` and the `SECRET_KEY` from config.

**`get_current_user` (FastAPI dependency)**
Reads the `Authorization: Bearer <token>` header from the incoming request, decodes and verifies the JWT using the same `SECRET_KEY`, and returns the payload as a dict. Raises `HTTP 401` on any failure — missing header, expired token, invalid signature.

Start the service once both functions are implemented:

```bash
cd services/auth-service
uvicorn app.main:app --reload --port 8005
```

Get a token and verify it:

```bash
curl -X POST http://localhost:8005/v1/auth/token \
  -d "username=testuser&password=password"
```

Paste the returned token at **jwt.io** and find these three claims in the decoded payload:
- `sub` — who is this token for?
- `role` — what is this user allowed to do?
- `exp` — when does it expire?

You can also verify both functions together with the `/v1/auth/me` endpoint:

```bash
# Replace <token> with the value from the previous curl
curl http://localhost:8005/v1/auth/me -H "Authorization: Bearer <token>"
```

This is the information every service in the system can now read from any incoming request — without ever calling `auth-service` again. That is why the gateway can validate tokens locally.

---

## Part B — Register auth-service and lock the gateway *(~35 min)*

Open `gateway/app/config.py` and `gateway/app/main.py` — the lines for `auth-service` are already there, commented out with `# Added in Module 6`. Uncomment them.

Then open `gateway/app/main.py` and add JWT validation to the catch-all proxy route:

- Read the `Authorization: Bearer <token>` header
- Verify it using the shared `SECRET_KEY` (already in `gateway/app/config.py` — same value as auth-service)
- Missing or invalid token → return `401` immediately, do not forward
- Valid token → forward the request as before
- `/v1/auth/token` must stay **public** — you cannot require a token to get a token

Test it:

```bash
# Rejected at the gateway — no token
curl http://localhost:8000/v1/games

# Get a token
curl -X POST http://localhost:8000/v1/auth/token \
  -d "username=testuser&password=password"
# Copy the access_token value → YOUR_TOKEN

# Forwarded — valid token
curl http://localhost:8000/v1/games -H "Authorization: Bearer YOUR_TOKEN"
```

> If you have `jq` installed you can chain these in one line:
> `TOKEN=$(curl -s -X POST http://localhost:8000/v1/auth/token -d "username=testuser&password=password" | jq -r .access_token)`

---

## Part C — Role enforcement in game-service *(~20 min)*

The gateway checks identity. It does not check what a user is allowed to do — that is the service's responsibility.

Open `game-service/app/security.py` — the `require_admin` dependency is already fully implemented. Your only task is to:

1. Add `auth_secret_key` to `game-service/app/config.py` — it must match the `SECRET_KEY` in auth-service
2. Wire `require_admin` as a dependency on `DELETE /v1/games/{id}` in `game-service/app/routes.py`

Test with a gamer token (should get `403`) and an admin token (should succeed):

```bash
# 403 — valid token, wrong role
curl -X DELETE http://localhost:8000/v1/games/some-id \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get an admin token
curl -X POST http://localhost:8000/v1/auth/token \
  -d "username=admin&password=adminpass"
# Copy the access_token → ADMIN_TOKEN

# 200 — admin token, correct role
curl -X DELETE http://localhost:8000/v1/games/some-id \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

The gamer gets `403 Forbidden`, not `401 Unauthorized`. Make sure you understand why before moving on.

---

## Part D — Machine-to-Machine (M2M) token *(~10 min)*

`activity-service` calls `user-service` internally. Now that the gateway validates tokens, that internal call needs one too — but it is not acting on behalf of any user.

`activity-service` is already registered in `auth-service/app/users.py` with role `service`. The M2M client is scaffolded in `activity-service/app/infrastructure/auth_client.py`.

Read through `auth_client.py` to understand how it works, then confirm that creating an activity through the gateway still works with the token lock in place.

---

## Discussion *(~10 min)*

- You implemented `create_access_token`. The gateway verifies tokens using only the `SECRET_KEY` — never by calling `auth-service`. Why does that work, and what does it tell you about JWTs?
- The gateway checks identity. The service checks role. Why are those two responsibilities in different places?
- Why must `/v1/auth/token` stay public even though everything else requires a token?

---

## Minimum to submit this branch

- [ ] `create_access_token` and `get_current_user` implemented and working
- [ ] `auth-service` running and issuing valid tokens
- [ ] Gateway returns `401` for requests without a valid token
- [ ] `/v1/auth/token` remains public
- [ ] `DELETE /v1/games/{id}` returns `403` for gamer role, succeeds for admin role
- [ ] M2M internal calls still work after gateway is locked
- [ ] `REFLECTION.md` completed and committed

If you run out of time: Parts C and D are optional. Parts A and B are the core of this module.
