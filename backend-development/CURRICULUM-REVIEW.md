# backend-development - Curriculum Review (Phase 1)

Status: **APPROVED 2026-08-24** (decisions 1-4 below). Live curriculum and progress: [CURRICULUM.md](CURRICULUM.md).
Authoring rules: [AUTHORING-GUIDE.md](AUTHORING-GUIDE.md).

## Approved decisions
1. Replaced the original 19-folder scaffold with the 20-folder layout `01-http-web-fundamentals` ... `20-production-projects`.
2. Module 17 re-scoped from "re-teach the data layer" to "diagnose and scale"; near-duplicate pairs merged
   (stampede/herd/avalanche; Clean+Hexagonal; Gateway+BFF; delivery-semantics trio; 2PC+distributed tx;
   16.7 CORS folded into 01.9 + 16.12). Projects consolidated to 5 + optional reliability lab.
3. Docker Swarm stays as the orchestration target; Kubernetes deferred to `system-design`.
4. Scale confirmed at ~261 notebooks.

## Relationship to modern-python
- Hard prerequisites: 10 (SQL, SQLAlchemy), 11 (sockets/HTTP), 12 (asyncio), 15 (pytest, logging), 18 (APIs as a client).
- Never re-taught: Python syntax, dataclasses, decorators, context managers, exceptions, asyncio mechanics,
  pytest basics, mocking, logging config, typing, packaging, profiling basics, SQL syntax, SQLAlchemy CRUD,
  REST as a client, pydantic basics.
- Verified gaps (grep, not README): `contextvars`, `asyncio.Lock/Queue`, `pydantic-settings`, pydantic v2
  serialisation side, server-side HTTP/ASGI, password hashing. All covered inside backend notebooks
  (04.4, 04.5, 03.4/07.9, 01.1/03.1, 08.15). **No edits to modern-python required.**

## Additions vs the original brief
HTTP caching (01.4) · reverse proxies/X-Forwarded (01.10) · ASGI/uvicorn (01.1, 03.1) · bulk/PATCH (02.7) ·
sync-vs-async endpoints (03.6) · contextvars (04.4) · key choice/UUIDv7, upsert, SKIP LOCKED, bloat/vacuum,
pg_stat_statements (05) · bulk ops/raw SQL, driver choice (06.7, 06.11) · cookie security, revocation, API keys,
account flows (08) · resumable uploads (09.5) · Redis client hygiene (10.6) · scheduled jobs, job status (11.8, 11.16) ·
test factories, migration tests (13) · Python-in-container, migrations in pipeline, rollback (14) · bulkheads/load
shedding, incident response (15.17, 15.18) · BOLA/BFLA, DoS hygiene, audit logging, supply chain (16) ·
server tuning, replica lag, capacity (17) · clocks/IDs, idempotency end-to-end (19.4, 19.8).

## Boundary with system-design (kept overview-depth here)
17.13 sharding · 19.12 replication/leaders/consensus · 10.17 Sentinel/Cluster · 18.8/18.9 EDA/CQRS · 19.11 event sourcing.

## Corrections
02.9 teaches RFC 9457 (obsoletes RFC 7807).

## Rate-limiting split (three notebooks, deliberately)
02.12 = API contract (429, Retry-After, RateLimit-*) · 10.13 = algorithms + Redis implementation · 16.9 = abuse/DoS posture.

## Critical path
01 → 02 → 03 → 04 → 05 → 06 → 07 → 10 → 11 → 13 → 14 → 15 → 18 → 19 → 20. Modules 08, 09, 12, 16, 17 branch off it.
Known forward dependencies (deliberate, documented in the module READMEs): 08 uses Redis (10) for
sessions/denylists — read 10.14 alongside 08.1; 09 forward-references 11 for processing pipelines.

## Technology Tradeoffs (mandatory comparisons)
Referenced from AUTHORING-GUIDE §3 (PATTERN/DESIGN). Each comparison is owned by exactly one
notebook; other notebooks link to it rather than re-comparing.

| Comparison | Owned by |
|---|---|
| REST vs RPC vs GraphQL vs gRPC | 02.2 |
| Offset vs cursor vs keyset pagination | 02.5 |
| 202+polling vs webhooks vs SSE | 02.10 |
| Sync vs async endpoints (threadpool vs event loop) | 03.6 |
| Optimistic vs pessimistic locking | 05.13 |
| Sync vs async SQLAlchemy — psycopg3 vs asyncpg | 06.7 |
| Sessions vs JWT | 08.1 |
| Presigned URLs vs proxy-through-backend | 09.2/09.3 |
| Cache-aside vs write-through vs write-behind | 10.2–10.4 |
| Redis Pub/Sub vs Streams | 10.15 |
| ARQ vs Celery | 11.4 |
| Queue vs Pub/Sub vs Streaming | 11.9 |
| RabbitMQ vs Kafka vs NATS | 11.10 |
| WebSocket vs SSE vs long polling | 12.6 |
| Blue-green vs canary vs rolling | 14.13–14.15 |
| Vertical vs horizontal scaling | 17.9 |
| Monolith vs modular monolith vs microservices | 18.1 |

## Re-review 2026-08-29
Design re-validated end to end against the repo; structure, numbering (261 notebooks), prereqs
(every modern-python reference checked against the actual notebook files) and dependency graph
all hold. **No structural changes.** All 29 written notebooks (01 full, 02 full, 03.1–03.6)
pass `check.py`. Scope notes for upcoming notebooks — mentions inside existing notebooks, not
new numbers:
- **05.3** — teach money as `NUMERIC`/`Decimal` and `timestamptz` conventions as modelling
  decisions (the guide already mandates them in examples; make the *why* explicit here).
- **08.16** — MFA overview must include passkeys/WebAuthn (mainstream 2025–26 adoption).
- **11.15** — mention CDC (Debezium-style) as the alternative to a polling outbox relay.
- **15.11** — mention error-tracking tools (Sentry-style) as a complement to metrics alerting.

## 2026-27 currency and the AI-engineering bridge (2026-08-29)
The curriculum was re-checked against the current production stack (FastAPI 0.14x, SQLAlchemy
2.0.4x + asyncpg, Alembic, PostgreSQL 18) and against what a follow-on `ai-engineering` module
will assume. The async-first architecture taught in 03/04/06 **is** the 2026 standard; no
structural change. Currency scope notes (in-notebook, no renumbering):
- **05.8** retitled to "Search in Postgres - full-text and pgvector basics": FTS as before,
  plus pgvector as a Postgres extension — vector columns, HNSW index, one similarity query,
  and *when Postgres is enough vs a dedicated vector DB*. RAG pipelines, embeddings and
  retrieval quality stay in `ai-engineering`.
- **04.7 / 17.7** — `> Version note` on free-threaded CPython (3.13 experimental → 3.14
  supported): what changes in the "threads don't help CPU-bound work" story, and why
  production guidance in 2026 still defaults to the GIL build.
- **08.7** — teach OAuth2 through the OAuth 2.1 consolidation (PKCE everywhere, no implicit
  grant), naming 2.0 RFCs only as history.
- **14.3 / 14.10** — use `uv` in the multi-stage Dockerfile and CI examples (2026 default;
  `uv sync --frozen` in builds), with a one-line note on pip-only environments.
- SQLModel considered and rejected as primary stack: it hides the session/loading-strategy
  mechanics that modules 06's incidents exist to teach. One-line mention in 06.1.

**What `ai-engineering` (next track) will assume from here — and what therefore stays OUT of
backend-development:** token streaming rides on 02.10/03.11/12.4 (SSE) and 12 (WebSockets);
model-call resilience on 04.3/04.8 + 15.13-15.16 (timeouts, retries, fallback, degradation);
inference queues and batch jobs on 11 (backpressure, DLQs, job status); vector search intro on
05.8; cost/latency observability on 15; abuse and quota control on 02.12/10.13/16.9.
Excluded here by design: RAG architecture, embedding pipelines, model gateways/routing, agent
frameworks, MCP servers, evals, semantic caching, GPU serving. 12.4 (SSE) should explicitly use
a token-streaming-shaped example as its forward link.
