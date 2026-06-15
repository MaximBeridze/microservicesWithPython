# Module 5 — Reflection

**Team name**: _______________
**Branch**: `module-05/<team-name>`
**Submitted**: before Module 6 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

The game-service now has two models for the same data: SQLite for writes, Redis for reads. They store the same games in two different shapes.

**Why go through the trouble of maintaining two representations of the same data?**

Think about what kind of queries each model is optimised for, and what would happen if you tried to use the write model for high-traffic read operations.

We keep SQLite and Redis because they are useful for different jobs. SQLite is the write model, so it is the source of truth when a game is created or changed. Redis is the read model, so it can return a smaller game summary quickly.

This is useful when some data is read much more often than it is written. Instead of querying the full database every time, the service can serve a prepared summary from Redis.

---

## 2. Your choice

The logging-service checks GDPR consent before recording any activity. If a user has not opted in, the log is silently dropped.

**What does this consent check force you to accept about your data?** It is incomplete by design — some activities will never be recorded.

From a system design perspective: where is the right place to enforce this rule — in the logging-service, in the activity-service, or at the gateway? Why?

The consent check forces us to accept that the log data is incomplete by design. If a user has not opted in, their activity should not be stored in the logging-service, even if that would make analytics less complete.

The right place to enforce this is inside logging-service because logging-service owns the log data and the consent rules. The gateway should not decide what logging is allowed, and activity-service should not need to know the details of GDPR logging rules.

---

## 3. The tradeoff

With CQRS, your write model and read model can drift out of sync — a game is updated in SQLite but the Redis projection still shows the old data.

**In what scenario does this inconsistency matter to the user? In what scenario is it completely acceptable?**

Is there a class of applications where eventual consistency is never acceptable? What are they?

The inconsistency matters if the stale Redis summary shows something the user cares about right now, like an old title, wrong cover image, or wrong platform. The user might notice that one endpoint shows updated data while another still shows the old version.

It is acceptable when the data is not critical and can be slightly stale, like a game summary used for a feed or preview card. Eventual consistency is not acceptable for things like payments, account security, medical records, or legal consent state, where showing old data could cause real harm.

---

*Keep this file. You will refer back to it during the oral presentation.*
