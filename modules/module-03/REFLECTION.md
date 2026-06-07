# Module 3 — Reflection

**Team name**: _______________
**Branch**: `module-03/<team-name>`
**Submitted**: before Module 4 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

All client requests now go through the gateway. No client ever calls a service directly.

**Why does that single entry point exist? What would the client's life look like without it?**

Think about what the client would need to know and manage if it talked to each service on its own port.

The gateway exists so the client has one entry point into the system. Instead of the client needing to know that users are on port 8001, games are on port 8002, and activities are on port 8003, it only needs to call port 8000 and use the correct path.

Without the gateway, the client would need to manage service locations itself. That would make the frontend more tightly connected to the backend structure. If a service moved to a different port or was renamed, the client might need to change too. With the gateway, the client can stay simpler because routing decisions happen on the backend side.

The gateway also gives the system a place to add shared behavior later, such as authentication, version checks, or circuit breaking, without putting that same logic into every service.

---

## 2. Your choice

The activity-service makes two outbound calls: one to validate the user (with retry logic), one to fetch game data (with a null fallback if it fails).

**Why are these two calls treated differently? Why does one retry and the other just give up gracefully?**

What is the consequence for the user in each case if the downstream service is unavailable?

The validation call and the enrichment call are treated differently because they have different importance.

Validating the user is critical. If `activity-service` cannot confirm that the user exists, it should not create the activity. Otherwise the system could save activities for users that do not exist, which would make the data unreliable. That is why the user validation call retries once on a network error and returns an error if it still cannot reach `user-service`.

Fetching game data is optional. The activity can still be valid even if the game details cannot be loaded at that moment. If `game-service` is unavailable, the activity is still saved and the response returns `"game": null`. The user loses the enriched game details in the response, but their action is not blocked.

So the difference is about consequences. Failed user validation could corrupt the activity data, while failed game enrichment only makes the response less detailed.

---

## 3. The tradeoff

Every time a client creates an activity, three services are involved synchronously. They all have to be running, healthy, and fast.

**What is the systemic risk of chaining synchronous calls like this?**

What happens to the user experience if the slowest service in the chain takes 3 seconds to respond?

The systemic risk of chaining synchronous calls is that the whole request becomes dependent on multiple services being available and fast at the same time. Creating an activity now involves the gateway, activity-service, user-service, and sometimes game-service. If one critical service is slow or unavailable, the user feels that delay or receives an error.

If the slowest service in the chain takes 3 seconds to respond, the whole request can take at least 3 seconds, even if the other services are fast. From the user’s point of view, the system just feels slow. They do not care which service caused it.

This is the tradeoff of synchronous communication. It is simple to understand and gives immediate answers, but it can spread latency and failures across services. That is why it makes sense to use synchronous calls only when the answer is needed immediately, like user validation, and to allow graceful fallback for optional data like game enrichment.

---

*Keep this file. You will refer back to it during the oral presentation.*
