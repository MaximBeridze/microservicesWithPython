# Module 6 — Reflection

**Team name**: _______________
**Branch**: `module-06/<team-name>`
**Submitted**: before Module 7 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

The gateway now validates every JWT before forwarding a request. Individual services no longer need to check identity themselves.

**What does centralising authentication at the gateway buy you?** What would the alternative look like — if every service validated tokens on its own?

Think about what happens when you need to rotate the secret key, or add a new service to the system.

Centralising authentication at the gateway gives the system one front door. The client sends a JWT once, the gateway checks it, and invalid requests are rejected before they reach the services.

If every service validated tokens separately, the same logic would be repeated everywhere. Adding a new service would mean adding the same auth code again, and rotating the secret key would be easier to mess up because every service would need to be updated correctly.

---

## 2. Your choice

When activity-service calls user-service internally, it uses a Machine-to-Machine (M2M) token — not a user's token.

**Why can't it just reuse the user's token that arrived in the original request?**

What would break, or what door would you accidentally leave open, if services passed user tokens between themselves?

Activity-service should not reuse the user's token for internal calls because it is not acting as the user. It is acting as a service.

If services passed user tokens around, a downstream service might accidentally get more user permissions than it needs. It also makes it harder to tell whether an action was done by the user directly or by another service. A M2M token keeps that boundary clearer.

---

## 3. The tradeoff

The gateway and the auth-service share the same `SECRET_KEY` to verify tokens without making a network call on every request.

**What is the security risk of sharing this key?** What happens if it leaks?

And what would the alternative look like — verifying tokens by calling auth-service on every request instead? What does that cost you?

The risk of sharing the `SECRET_KEY` is that anyone with the key can forge valid tokens. If it leaks, an attacker could create their own admin token and bypass normal login.

The benefit is speed and independence: the gateway can verify tokens locally without calling auth-service on every request. The alternative is asking auth-service to validate every request, but that adds network latency and makes auth-service a bottleneck or single point of failure.

---

*Keep this file. You will refer back to it during the oral presentation.*
