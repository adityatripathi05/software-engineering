# AUTHORING GUIDE - how every `backend-development` notebook is written

This file is the **generation brief**. A model (or a person) producing any notebook in this
module must read this file, `CURRICULUM.md`, and the target module's `README.md` first, then
write one notebook at a time. It is written as instructions to the author.

---

## 0. Who you are and what you are producing

You are a **senior backend engineer writing for another engineer** who already knows Python well
(they have finished `modern-python/`, 107 notebooks) and can make things work. Your job is to teach
them to make it **reliable, secure, observable, scalable and maintainable in production**.

You are NOT writing: a tutorial, a framework reference, a blog post, a listicle, a textbook chapter.
Test for every paragraph: *would a staff engineer say this to a mid-level engineer in a design
review or an incident retro?* If not, cut it.

The reader's central question is always:

> "I know how to make this work. Now teach me how to make it reliable, secure, observable,
> scalable and maintainable in production."

---

## 1. Process - before writing a single line

1. Open `CURRICULUM.md`; find the notebook id (e.g. `05.9`). Note its **difficulty**, **module
   prerequisites** and **dependencies**.
2. Open the module `README.md` and the *previous* notebook in the same module (if it exists) so
   terminology and the running example stay continuous.
3. Open the `modern-python` notebooks listed as prerequisites. **Skim their headings.** Anything
   taught there is *referenced*, never re-taught (see §6).
4. Decide the **one running system** the examples will live in (see §4). Prefer the module's
   running example; do not invent a new domain per notebook.
5. Write the notebook to the template in §2. Then run the checklist in §9.
6. Run `python backend-development/_tools/check.py 05.9`. It verifies the mechanical rules —
   required headings, header block, prose length for the level, banned/deprecated APIs inside
   code, block length, stacked listings — so review attention goes to what only a human can
   judge: is the incident realistic, and is the example real-dev rather than bookish?
7. Update `_tools/curriculum.py` → `STATUS["05.9"] = "draft"` and run
   `python backend-development/_tools/build.py`.

Write **one notebook per response**. Never batch a module into one response.

---

## 2. The template (mandatory - every heading, in this order)

```markdown
# 05.9 Connection Pooling and PgBouncer

> **Prerequisites:** modern-python 10.2 (DB-API, who commits) · 04.3 (async clients and pools)
> **What you'll learn:** 3-5 bullets, each a capability ("size a pool from first principles"),
> not a topic ("pool sizing").
> **Level:** Intermediate

## Concept
### Plain-English Explanation
### Technical Explanation
### Mental Model

## How It Works
(internals, sequence, lifecycle - diagrams in fenced ```text blocks are encouraged)

## Code Example
(only where code genuinely demonstrates the concept - see §4 and §5)

## Design Patterns / Tradeoffs
(for each approach: how it works · advantages · disadvantages · failure modes ·
 when to use · when NOT to use - as prose or a comparison table, then a recommendation)

## Production Scenario
### Symptoms
### Diagnosis
### Root Cause
### Fix
### Prevention

## Failure-First Checklist
(the "what happens if..." questions that apply to THIS topic, each answered in one line)

## Common Pitfalls
(anti-patterns: what people do · why it breaks · what to do instead)

## How to Test This
(2-6 lines: what a unit/integration/failure test for this topic looks like - from 03 onward)

## Interview Questions
(5-8, ranging from "explain" to "design" to "debug this"; give the answer shape in one line each)

## Key Takeaways
(5-8 bullets - decisions, not definitions)

## Related
(backward links to modern-python and earlier backend notebooks; forward links to where the
 topic is picked up again; one line each, with the reason)
```

Rules on the template:
- Headings are exact. Tools and readers depend on them.
- Omit **Code Example** only for purely conceptual notebooks (e.g. 19.5 CAP, 18.2 when-not-
  microservices) and say why in one line under the heading. Never omit **Production Scenario**.
- **Failure-First Checklist** and **How to Test This** are additions to the original brief's
  template; they are mandatory because they encode the cross-cutting principles.
- Use `⚠️` for a genuine trap - something that runs but does the wrong thing (repo convention).
- Use a `> **Version note**` callout when behaviour differs across Python 3.12/3.13/3.14,
  SQLAlchemy 2.0/2.1, Pydantic 2.x minors, PostgreSQL 16/17/18, FastAPI minors. Only when true.

---

## 3. The three depths - what each section must actually contain

### CONCEPT
- *Plain-English*: one short paragraph a non-engineer could follow; an analogy only if it is
  exact (a leaky analogy is worse than none).
- *Technical*: what it is, why it exists, what problem it solves, how it works internally, the
  terminology (bold each term on first use), and the numbers that matter (default pool size,
  TCP handshake RTTs, typical p99 budgets). Numbers make it real.
- *Mental Model*: one or two sentences the reader can carry. ("A pool is a semaphore around
  expensive objects; sizing it is deciding how many concurrent DB conversations you are willing
  to have, not how many requests you serve.")

### PATTERN / DESIGN
Compare **real alternatives** that engineers actually choose between. For each: how it works,
advantages, disadvantages, *failure modes*, when to use, when NOT to use. End with a
recommendation and the condition under which you'd change it. Never present a technology as
universally better. Mandatory comparisons are listed in `CURRICULUM-REVIEW.md` §Technology
Tradeoffs (ARQ vs Celery, RabbitMQ vs Kafka vs NATS, Pub/Sub vs Streams, REST vs gRPC, ...).

### PRODUCTION SCENARIO
This is non-negotiable and is the section most likely to be written badly. Requirements:

- It is a **specific incident**, with a time, a trigger, and a blast radius. Not "the pool may
  run out"; rather "Tuesday 09:40, marketing sends a push notification, `/v1/feed` p99 goes from
  120 ms to 8 s, 503s begin at 09:43."
- **Symptoms** are what the on-call *sees*: the alert text, the dashboard shape, the log lines,
  the user-facing effect. Quote realistic log lines and metric names
  (`http_server_request_duration_seconds{route="/v1/feed",le="1"}`, `pg_stat_activity` counts,
  `sqlalchemy.pool QueuePool limit of size 5 overflow 10 reached, connection timed out`).
- **Diagnosis** follows the observability ladder, explicitly:
  `Alert → Metrics → Logs → Trace → Dependency health → DB/Redis/Queue metrics → Root cause`.
  Show which *signal* eliminated which *hypothesis*. Engineers must learn to reason from
  telemetry, not from reading source code.
- **Root Cause** is one or two sentences and is *mechanistic* ("each request held a connection
  across an outbound 3 s HTTP call, so 20 concurrent requests pinned all 20 connections").
- **Fix** is split into *mitigation now* (what stops the bleeding in 5 minutes) and *permanent
  fix* (the code/config change, shown). Both are required.
- **Prevention** names the metric/alert/test/review rule that would have caught it earlier.

A scenario that could be pasted into any notebook is a failed scenario.

---

## 4. Examples must come from real development - the core quality rule

The difference between a bookish notebook and a useful one is almost entirely the examples.

### 4.1 Use one running system per module
Every module picks a realistic product and sticks to it so the reader accumulates context:

| Module | Running system (default - keep unless a topic genuinely needs another) |
|---|---|
| 01, 02, 03 | A B2B SaaS **invoicing API** (`/v1/invoices`, `/v1/customers`, PDF generation, webhooks to customers' systems) |
| 04 | The same invoicing API under load; outbound calls to a tax-rate provider and a PDF renderer |
| 05, 06, 07 | **Multi-tenant ticketing/helpdesk** (tenants, agents, tickets, comments, attachments; heavy list queries) |
| 08, 16 | The ticketing product's **auth service** (agents, customers, SSO for enterprise tenants, API keys for integrations) |
| 09 | Ticket **attachments** (screenshots, log bundles up to 2 GB) |
| 10 | Ticketing **dashboards** (per-tenant counters, agent presence, expensive aggregate views) |
| 11 | Ticketing **notifications and SLA timers** (email on assignment, SLA-breach escalations, nightly digests) |
| 12 | **Agent console** live updates (ticket updated by someone else, typing indicators, presence) |
| 13, 14, 15, 17 | The ticketing system as deployed - same code, now in compose/Swarm, with CI, metrics, traces |
| 18, 19 | Ticketing grown into **orders + payments + notifications** services (the seams that break) |
| 20 | As specified per project in `CURRICULUM.md` |

A topic may use a *second* system only when the default cannot show the point honestly
(e.g. 05.17 partitioning wants time-series events - use the NMS alarm table from Project 5).

### 4.2 What "real dev example" means - with pairs
Each pair: the left is rejected, the right is what we want.

| ✗ Bookish (reject) | ✓ Real-dev (write this) |
|---|---|
| `class Item(BaseModel): name: str; price: float` | `class InvoiceLineIn(BaseModel)` with `Decimal` money, `quantity: PositiveInt`, `tax_code: Literal[...]`, and a `model_validator` that rejects negative totals - because floats for money is the bug you're preventing |
| `@app.get("/items/{item_id}")` returning a dict | `@router.get("/invoices/{invoice_id}", response_model=InvoiceOut)` that goes through a service, checks tenant ownership, and returns `404` (not `403`) for another tenant's invoice - and the notebook says *why 404* |
| `time.sleep(2)` to "simulate slow work" | `await tax_client.rate_for(address)` with `httpx.Timeout(connect=1, read=3)`, showing what the event loop does while it waits - and what happens when that timeout is missing |
| `users = session.query(User).all()` then loop | The agent-inbox query that loads 50 tickets and then triggers 50 `ticket.requester` lazy loads - with the SQL echo output showing the 51 statements, then `selectinload` and the 2 statements |
| `cache.set("key", value)` | `cache.get_or_compute(f"tenant:{tid}:dashboard:v3", ttl=60±jitter, lock=...)` with key versioning, jitter, and the stampede guard - because the naive version is what caused the incident in §Production Scenario |
| `def add_numbers(a, b)` unit test | A test that starts Postgres in Testcontainers, runs Alembic to head, inserts two tenants, and asserts tenant A cannot read tenant B's ticket through the public API |
| "Worker processes the job" | `async def send_assignment_email(ctx, ticket_id: UUID, *, idempotency_key: str)` that checks a `sent_notifications` unique key *before* calling the email provider, with the retry policy that makes it safe |
| `docker run python app.py` | A multi-stage Dockerfile with a non-root user, `tini`, `uvicorn --workers` derived from CPU count, and a `HEALTHCHECK` that hits `/ready` - then the incident where `/health` passed while the DB was unreachable |

Heuristics that produce real-dev examples:
- **Start from the bug or the incident, then show the code that prevents it.** Code exists to
  make a failure concrete, not to fill the section.
- **Show what the machine shows.** SQL echo, `EXPLAIN ANALYZE` output, log lines, metric
  names, `docker stats`, `pg_stat_activity`, a trace waterfall in ASCII. Real output is the
  difference between "trust me" and "see for yourself".
- **Use real constraints**: tenants, money as `Decimal`, time as timezone-aware UTC, IDs as
  UUID (v7 when ordering matters), soft-delete vs hard-delete, audit columns, retries that
  have to be idempotent.
- **Name the layer** each snippet lives in (`routers/`, `services/`, `repositories/`,
  `workers/`) from module 07 onward, matching the structure taught in 03.1 and 07.1.
- **Show the before and the after** when the topic is a fix (N+1, pool, stampede, migration):
  the broken version, the evidence it is broken, the fixed version, the evidence it is fixed.
- **Never** use foo/bar/baz, Item/Widget, `user1`, `test123`, `example.com` as the *subject*
  (as a sample hostname in a config it's fine).

### 4.3 Code rules
- Python 3.12+ syntax: `type X = ...`, PEP 695 generics, `match` where it helps, `Self`,
  `StrEnum`, `datetime.now(UTC)`, `TaskGroup`, `asyncio.timeout`.
- Type hints everywhere. No `Any` without a comment.
- FastAPI: `APIRouter`, `Annotated[..., Depends()]`, `lifespan=`, `response_model`/return
  annotations, `HTTPException` only at the router layer, no `@app.on_event`.
- Pydantic v2: `model_validator`, `field_validator`, `ConfigDict`, `model_dump(mode="json")`,
  `TypeAdapter`; no v1 `class Config`, no `.dict()`, no `validator`.
- SQLAlchemy 2.x: `DeclarativeBase`, `Mapped[...]`/`mapped_column`, `select()`,
  `session.execute(...).scalars()`, `async_sessionmaker`; no `query()`, no `declarative_base()`.
- Alembic: explicit `op.*` migrations; autogenerate is reviewed, never trusted.
- Redis: `redis.asyncio`, explicit `socket_timeout`, connection pool, `SET ... NX EX`, Lua for
  atomic multi-key ops when needed.
- Tests: pytest, `pytest-asyncio` (or `anyio`), `httpx.AsyncClient(transport=ASGITransport(...))`,
  Testcontainers for Postgres/Redis/RabbitMQ; `respx` for HTTP doubles.
- Every snippet is **complete enough to run** given the module's compose file, or is explicitly
  marked `# sketch - not runnable` with the reason. No `...` bodies inside functions that matter.
- Keep listings short: 10-40 lines, and *every* listing is followed by prose that says what to
  look at and why. A 120-line listing with no commentary is a defect.
- Show the shell where it matters: `EXPLAIN (ANALYZE, BUFFERS)`, `redis-cli --hotkeys`,
  `docker compose logs -f worker`, `curl -i` for headers.

---

## 5. Diagrams and pseudo-code
For conceptual topics prefer an ASCII diagram in a ```text block over code. Diagrams must show
the **mechanism** (sequence, who holds what, where time goes), not just boxes with names. Label
the arrows with what crosses them (bytes, a connection, a lock, a message id). Sequence diagrams
for request flows and failure timelines are especially valuable:

```text
t=0ms   client ──POST /invoices──▶ uvicorn ──▶ handler
t=2ms                                   handler ──SELECT customer──▶ PG   (conn #7 checked out)
t=5ms                                   handler ──POST /rate──▶ tax-api  (conn #7 still held!)
t=3005ms                                tax-api times out ──▶ handler
t=3006ms                                handler ──rollback──▶ PG          (conn #7 returned)
```

---

## 6. Referencing `modern-python` and earlier backend notebooks
- Reference by number and title: "*see modern-python 12.5 asyncio (Timeouts)*",
  "*built in 06.8 Connection pool configuration*".
- When a prerequisite idea is needed, give a **one-sentence recap** and the link; do not
  re-teach. If the recap would exceed three sentences, the prerequisite is wrong - fix the
  prerequisite list instead.
- The following are **never re-taught**: Python syntax, dataclasses, decorators, context
  managers, exceptions, asyncio mechanics, pytest basics, `unittest.mock`, logging handlers,
  type hints, packaging, cProfile, SQL syntax, SQLAlchemy CRUD, REST as a client, pydantic
  model basics.
- Forward references are fine and encouraged ("rate limiting *algorithms* are 10.13; here we
  define only the contract").

---

## 7. Cross-cutting principles - must be visible, not just mentioned
Every notebook where they apply must *use* these, in the examples and the scenario:

- **Reliability ladder**: timeout → retry → backoff + jitter → circuit breaker → bulkhead →
  graceful degradation. Retries without a budget make outages worse; say so where relevant.
- **Idempotency**: HTTP, payments/orders, jobs, consumers, webhooks, distributed systems.
- **Observability**: logs, metrics, traces - diagnosis is always telemetry-first.
- **Failure-first**: the checklist section answers the applicable questions from:
  DB slow / DB down / Redis down / queue down / worker crashes / network timeout / request
  retried / same message twice / dependency returns 500 / traffic ×10 / one instance unhealthy.

---

## 8. Explicit anti-patterns to call out (where relevant)
Fat route handlers · global DB session · unbounded retries · retrying non-idempotent ops ·
Redis for everything · microservices too early · async for CPU-bound work · blind ORM usage ·
ignoring pool limits · OFFSET pagination at scale · returning ORM models from endpoints ·
secrets in images · logging tokens/PII · mocks-only test suites · `/health` that only returns
200 · catching `Exception` and continuing · `except: pass` around commits · float money ·
naive datetimes · `SELECT *` in hot paths · N+1 hidden by lazy loading · JWT without `exp` or
with `alg: none` · CORS `*` with credentials · trusting `X-Forwarded-For` blindly.

For each: what people do · why it breaks (mechanism) · what to do instead.

---

## 9. Pre-submit checklist (run it; do not skip)
- [ ] All template headings present, exact, in order; header block filled.
- [ ] Examples live in the module's running system (§4.1); no foo/bar/Item.
- [ ] At least one snippet shows *real output* (SQL, logs, metrics, EXPLAIN, headers).
- [ ] Every listing ≤ 40 lines and followed by explanation; modern syntax per §4.3; no deprecated APIs.
- [ ] Tradeoffs section compares ≥ 2 genuine alternatives with when/when-not.
- [ ] Production Scenario: specific incident · symptoms as seen on-call · diagnosis via the
      telemetry ladder · mechanistic root cause · mitigation + permanent fix · prevention.
- [ ] Failure-First checklist answers the applicable questions.
- [ ] Reliability / idempotency / observability principles used, not name-dropped.
- [ ] Prereqs referenced, not re-taught; Related section has backward and forward links.
- [ ] Interview questions include at least one "debug this" and one "design this".
- [ ] Length (prose only, excluding code blocks and tables): Beginner 1600-3000 ·
      Intermediate 2000-3200 · Advanced 2400-3800. Calibrated against module 01 — the template
      has ~17 required headings, and below the lower bound a section becomes a stub rather than
      teaching. Longer is not better; denser is.
- [ ] No code block over 55 lines; no 3 consecutive blocks without prose between them
      (a shell command plus its output counts as one unit).
- [ ] `python backend-development/_tools/check.py <ID>` passes.
- [ ] `STATUS` updated in `_tools/curriculum.py`; `build.py` run.

---

## 10. Per-notebook generation prompt (copy, fill, run)

```text
Read backend-development/AUTHORING-GUIDE.md, backend-development/CURRICULUM.md and
backend-development/<MODULE>/README.md. Skim the headings of the modern-python prerequisite
notebooks listed for <ID>.

Write notebook <ID> "<TITLE>" to backend-development/<MODULE>/<FILENAME>.md.

Constraints:
- Level: <B/I/A>. Running system: <from §4.1>. Previous notebook in module: <ID-1> (keep its
  terminology and examples continuous).
- Follow the template in AUTHORING-GUIDE §2 exactly. Apply §3 depth rules, §4 example rules,
  §7 principles, §8 anti-patterns. Run the §9 checklist before finishing.
- The Production Scenario must be a specific incident diagnosed via Alert → Metrics → Logs →
  Trace → Dependency health → Root cause, with mitigation and permanent fix.
- Do not re-teach anything in the "never re-taught" list (§6); reference it.
- One notebook only. Then run python backend-development/_tools/check.py <ID> and fix anything
  it reports; set STATUS["<ID>"] = "draft" in _tools/curriculum.py; run
  python backend-development/_tools/build.py.
```

## 11. Per-module generation loop
For a module: generate notebooks in order, one per response, each reading the previous one
first. After the last notebook, write a `_recap.md` in the module folder — what was built, a
table of the incidents with the general lesson each carries, any configuration invariants
established, and what the next module assumes. `build.py` appends it below the generated table
in the module README and preserves it across regenerations. Then set all statuses to `review`
and run `python backend-development/_tools/check.py <NN>` for the whole module. A reviewer reads
the module end-to-end for continuity of the running system and promotes to `done`.

**Worked example:** module 01 is complete and conforms. Use
[01.3](01-http-web-fundamentals/01.3-status-codes-and-headers.md) as the reference for the
template and the production-scenario depth, and
[01-http-web-fundamentals/_recap.md](01-http-web-fundamentals/_recap.md) as the reference recap.
