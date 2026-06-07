# Module 2 — Reflection

**Team name**: _______________
**Branch**: `module-02/<team-name>`
**Submitted**: before Module 3 lesson

---

Answer the three questions below. There are no right or wrong answers — we are looking for your reasoning, not a textbook definition. A few honest sentences are worth more than a long generic paragraph.

---

## 1. The "why"

You built a service with distinct layers: models, schemas, repository, service, and routes — each with a single responsibility.

**Why not just put everything in one file and call it done?**

Think about what happens six months later when someone new joins the team, or when you need to swap SQLite for PostgreSQL. What does the layered structure protect you from?

Putting everything in one file would be faster at the beginning, but it would become harder to understand and change later. The layered structure makes each part of the service responsible for one job. The model defines the database table, the schema defines what the API accepts and returns, the repository handles database queries, the service contains business logic, and the routes handle HTTP requests.

This protects the code from becoming tangled. For example, if the project switches from SQLite to PostgreSQL, most of the change should stay near the database/repository/migration layer instead of spreading through every route. It also helps a new developer know where to look. If an endpoint returns the wrong status code, they check routes. If a query is wrong, they check repository. If the returned JSON shape is wrong, they check schemas.

---

## 2. Your choice

Each service owns its data exclusively — no other service is allowed to touch its database directly.

**Pick one entity your service owns (e.g. `User`, `Game`). What would go wrong if another service could write to that table directly?**

Give a concrete scenario, not a general principle.

The `game-service` owns the `Game` entity. Other services should not be able to write directly to the `games` table.

A concrete example would be `activity-service` recording that a user played a game. It might need to reference a `game_id`, but it should not directly insert or update games. If it could write to the `games` table, it might create duplicate games, use a different title format, or change a platform/genre in a way that breaks search results. Then the game catalogue would become inconsistent because there would be more than one place deciding what a valid game record looks like.

The safer design is for `game-service` to be the only service that creates and changes games. Other services can call it through an API or use its IDs, but they should not bypass its rules by touching the database directly.

---

## 3. The tradeoff

You now have models, schemas, a repository, a service, and routes — five layers for what is essentially a CRUD service.

**For a system this small, what is the cost of all this structure?**

And at what point does the complexity start to pay off? Where is the tipping point?

For a small CRUD service, the cost of this structure is that there are more files and more steps than feels necessary. Creating one endpoint means touching schemas, repository, service, routes, tests, and sometimes migrations. For a tiny project, that can feel slower than just writing the SQL and HTTP response in one file.

The structure starts to pay off when the service grows beyond simple CRUD. Once there are more endpoints, more validation rules, tests, database migrations, and other services depending on the API, the separation becomes useful. The tipping point is when changing one part of the service without breaking another part becomes more important than writing the first version quickly. In this project, that point comes fairly early because `game-service` is part of a larger microservices system, not a standalone script.

---

*Keep this file. You will refer back to it during the oral presentation.*
