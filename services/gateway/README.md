# gateway

Single entry point for all client requests from Module 3 onward. Routes by path prefix — no business logic.

## Setup

```bash
# From the repo root, copy this starter into place first:
cp -r modules/module-03/gateway-starter gateway

cd gateway
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Your task

Open `app/main.py` and implement the `proxy` function. The step-by-step instructions are in the docstring.

## Routing table

| Path prefix | Forwards to |
|---|---|
| `/v1/users/...` | user-service (port 8001) |
| `/v1/games/...` | game-service (port 8002) |
| `/v1/activities/...` | activity-service (port 8003) |
| `/health` | handled by the gateway itself |

New entries are added to `ROUTES` in `main.py` as each module introduces a new service.
