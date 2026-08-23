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
