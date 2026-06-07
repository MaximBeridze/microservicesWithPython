# Module 4 — Asynchronous Messaging

**Duration**: 2h in class
**Branch to submit**: `module-04/<team-name>`

---

## Objective

Until now, services communicated synchronously — one service called another and waited for a reply. This module introduces asynchronous messaging: a service drops a message into a broker and moves on, without waiting for any response.

You will wire one messaging flow into the system: when an activity is logged, `activity-service` publishes a message to RabbitMQ and `notification-service` consumes it.

---

## Before you start

Your module-03 work must be in place: gateway running on port 8000, `activity-service` working, seeded users and games available.

Start the RabbitMQ broker:

```bash
docker compose -f docker-compose.infra.yml up -d rabbitmq
```

Confirm it's up:
- RabbitMQ management UI: http://localhost:15672 (guest / guest)

Start `notification-service` in a separate terminal:

```bash
cd services/notification-service
npm install
npm run dev
```

Confirm it's up:
- http://localhost:8004/v1/notifications should return an empty list `[]`

---

## What's provided

- RabbitMQ is running via Docker. You do not need to configure it.
- `rabbitmq_publisher.py` is scaffolded in `services/activity-service/app/infrastructure/` — the connection and publish logic is done, you fill in the call site.
- `notification-service` is already built (Node.js) — you started it above.

Install the new dependency in `activity-service`:

```bash
cd services/activity-service
pip install -r requirements.txt
```

---

## Part A — Wire the RabbitMQ publisher *(~50 min)*

When a user logs an activity, a notification should be sent to `notification-service` via RabbitMQ.

Open `services/activity-service/app/infrastructure/rabbitmq_publisher.py` — the publisher is already implemented. Your job is to **call it** from the right place in `create_activity`.

After wiring it up, verify the full flow:

1. Log an activity through the gateway:
```bash
curl -X POST http://localhost:8000/v1/activities \
  -H "Content-Type: application/json" \
  -d '{"user_id": "YOUR_USER_ID", "game_id": "YOUR_GAME_ID", "action": "started"}'
```
2. Open the RabbitMQ UI at http://localhost:15672 — go to the **Queues** tab and confirm messages appeared in `gamehub.notifications` and `gamehub.logs`
3. Check the `notification-service` logs — a notification should appear

---

## Part B — Register notification-service in the gateway *(~20 min)*

`notification-service` is now part of the system. Add it to the gateway's routing table.

Open `gateway/app/config.py` and `gateway/app/main.py` — the lines for `notification-service` are already there, commented out with `# Added in Module 4`. Uncomment them.

Verify:
```bash
curl http://localhost:8000/v1/notifications
```

---

## Discussion *(~15 min)*

- What happens to the activity request if `notification-service` is down when the message is published? Should the activity creation fail?
- In Module 3, you called `game-service` directly over HTTP to enrich the response. Why not do the same for notifications — why introduce a broker at all?
- The activity is saved and the message is sent — but you have no confirmation the notification was delivered. What visibility do you lose compared to a synchronous call?

---

## Minimum to submit this branch

- [ ] Activity creation publishes a RabbitMQ message — visible in the management UI
- [ ] `notification-service` registered in the gateway and reachable via port 8000
- [ ] `REFLECTION.md` completed and committed
