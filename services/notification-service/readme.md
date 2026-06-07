# Notification Service

This service runs **locally** (Node.js), not in Docker. It listens for messages from RabbitMQ and stores them in a local SQLite database.

```
notification-service/
  ├── src/
  │   ├── index.ts       ← starts HTTP server + consumer
  │   ├── consumer.ts    ← RabbitMQ consumer → SQLite
  │   ├── db.ts          ← SQLite init
  │   └── routes.ts      ← GET /v1/notifications, GET /v1/notifications/:user_id
  ├── package.json
  ├── tsconfig.json
  └── .env.example
```

## Getting Started

### 1. Start RabbitMQ (via Docker)

RabbitMQ is the only dependency that needs Docker. From the **repo root**:

```bash
docker compose -f docker-compose.infra.yml up rabbitmq
```

This starts RabbitMQ on `localhost:5672`. You can also open the management UI at http://localhost:15672 (guest/guest) to inspect queues.

### 2. Install dependencies

```bash
cd services/notification-service
npm install
```

> On Windows, `better-sqlite3` requires native compilation. If `npm install` fails, make sure you have Python and a C++ compiler installed, or use [windows-build-tools](https://www.npmjs.com/package/windows-build-tools).

### 3. Configure environment

```bash
cp .env.example .env
```

The defaults work as-is if RabbitMQ is running with the standard guest credentials.

### 4. Run the service

```bash
npm run dev
```

The service starts on http://localhost:8004.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/v1/notifications` | All notifications (newest first) |
| GET | `/v1/notifications/:user_id` | Notifications for a specific user |

## How it works

1. On startup, the consumer connects to RabbitMQ and listens on the `gamehub.notifications` queue.
2. Each message must be JSON with the shape `{ "user_id": "...", "message": "..." }`.
3. Messages are persisted in a local `notifications.db` SQLite file (auto-created on first run).
4. The HTTP server exposes the stored notifications for other services or the frontend to read.
