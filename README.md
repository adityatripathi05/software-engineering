# Software Engineering

Self-paced engineering notes that are organised into tracks.

| Track | Status | Covers |
|---|---|---|
| [`modern-python/`](modern-python/) | **Complete** — 107 notebooks | The language and its ecosystem, from first principles to four end-to-end builds |
| [`backend-development/`](backend-development/) | **Curriculum approved** — 0/261 notebooks | Building one service correctly: HTTP, FastAPI, PostgreSQL, auth, caching, Docker, CI/CD |

Two further tracks — **system design** and cross-track **projects** — are part of the plan
and will appear here when work on them starts.

---

# modern-python

A complete, self-paced Python curriculum.

Written for **Python 3.12+**, with version notes wherever 3.13 / 3.14 behave differently.

## How to use these notes

Each folder is a topic. Notebooks are numbered in teaching order — work through them
top to bottom. Every notebook follows the same shape:

1. **Header** — prerequisites and what you'll learn
2. **Concept** — plain-English explanation, with an analogy where it helps
3. **Syntax breakdown** — the form, named part by part
4. **Examples** — runnable, simple → advanced
5. **Common Mistakes & Pitfalls**
6. **Best Practices** — PEP 8 and modern idioms
7. **Practice Exercises**

### Running the notebooks

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install jupyterlab
jupyter lab
```

Code cells are shipped **unexecuted** so the notebook shows you what *should* happen
rather than what happened on someone else's machine. Run them yourself.

> Some notebooks need extras (a database server, a GUI display, network access).
> Those state their requirements in the header cell.

## Curriculum map

All paths below are under [`modern-python/`](modern-python/).

| # | Folder | Covers |
|---|--------|--------|
| 00 | Books and References | Reference PDFs — Van Rossum's tutorial, Kuhlman, *Fluent Python*, *Architecture Patterns with Python* |
| 01 | Basic | Programming concepts, Python intro, REPL, syntax, I/O, operators |
| 02 | Datatypes | str, numbers, tuple, list, dict, set; mutability, copying, unpacking |
| 03 | Flow Control Statement | if/elif/else, `match`/`case`, loops, comprehensions, generators |
| 04 | Functions | Parameters, scope, closures, decorators, generators |
| 05 | OOPs | Classes, inheritance, MRO, dunder methods, ABCs |
| 06 | Exception Handling | try/except, custom exceptions, chaining, context managers |
| 07 | Module and Packages | Imports, packages, pip, venv, standard library |
| 08 | File Handling | Text, CSV, JSON, binary, `pathlib` |
| 09 | Regular Expression | The `re` module, patterns, groups |
| 10 | Database | SQL, `sqlite3`, MySQL/PostgreSQL, SQLAlchemy ORM, key-value and document stores, graph data |
| 11 | Socket Programming | Networking fundamentals, TCP framing, UDP, concurrent servers, HTTP and `requests` |
| 12 | Concurrency | The GIL, threading, multiprocessing, `concurrent.futures`, `asyncio` |
| 13 | How Python Works Under the Hood | Objects on the heap, names and identity, the call stack and frames, reference counting and the cyclic collector, `weakref`, object sizes and `__slots__`, descriptors and class creation |
| 14 | Data Structure and Algorithm | Complexity, Python's real costs, arrays and two pointers, linked lists, trees, graphs, sorting, DP, interview patterns |
| 15 | Testing and Debugging | `assert`, `unittest`, `pytest`, fixtures, mocking, coverage, property-based testing; tracebacks, `pdb`, debugging strategy, logging |
| 16 | Type Hints and Static Typing | `mypy`, narrowing, `Literal`, `TypedDict`, generics and variance, protocols, adoption |
| 17 | Tooling, Packaging and Environments | venv and pip, `pyproject.toml`, building and publishing, `ruff`, profiling |
| 18 | Working with APIs | REST semantics, auth and secrets, pagination and retries, `pydantic` validation, testing and concurrency |
| 19 | Capstone Projects | Four end-to-end builds: CLI task tracker, log-analysis pipeline, SQLite inventory service, concurrent API aggregator |

Every folder is complete and verified — the track is finished. See
[CHANGELOG.md](CHANGELOG.md) for the detailed build record.

## Conventions used in these notes

- **f-strings** are the default for formatting. `.format()` and `%` appear once, labelled *legacy*.
- **`pathlib`** is preferred over `os.path` for filesystem work.
- **Type hints** are introduced gradually and used in later folders.
- ⚠️ marks a genuine trap — something that runs but does the wrong thing.
- **Version note** callouts flag behaviour that differs across 3.12 / 3.13 / 3.14.

---

# backend-development

Curriculum approved (2026-08-24); notebooks are being written module by module.

- [CURRICULUM.md](backend-development/CURRICULUM.md) - all 20 modules, 261 notebooks, prerequisites, dependencies, difficulty and **live progress**
- [AUTHORING-GUIDE.md](backend-development/AUTHORING-GUIDE.md) - the standard every notebook is written to (template, depth rules, real-dev example rules, production-scenario rules)
- [CURRICULUM-REVIEW.md](backend-development/CURRICULUM-REVIEW.md) - design rationale and boundary with `system-design`

| # | Folder | Covers |
|---|--------|--------|
| 01 | http-web-fundamentals | Lifecycle, methods, status codes, HTTP caching, cookies, connections, TLS, CORS, proxies |
| 02 | api-design-patterns | Resources, REST/RPC/GraphQL/gRPC, versioning, pagination, idempotency, RFC 9457, webhooks, rate-limit contract |
| 03 | fastapi | ASGI, routing, Pydantic v2, DI, sync vs async endpoints, middleware, lifespan, streaming, deployment |
| 04 | async-concurrency | Event loop in a server, blocking I/O, contextvars, races, lost updates, timeouts, cancellation, shutdown |
| 05 | postgresql-data-modeling | Modelling, constraints, multi-tenancy, indexing, EXPLAIN, pooling, MVCC, locks, JSONB, partitioning, PITR |
| 06 | sqlalchemy-data-access | Engine/session lifecycle, loading strategies, N+1, async, pool config, repository/UoW, Alembic, zero-downtime migrations |
| 07 | backend-design-patterns | Layers, service/repository/UoW, DTO vs domain vs persistence, DI, configuration, when abstraction hurts |
| 08 | authentication-authorization | Sessions, cookies, JWT, refresh rotation, OAuth2/PKCE/OIDC, API keys, RBAC/ABAC, hashing, account flows, attacks |
| 09 | file-handling-object-storage | Presigned vs proxy uploads, S3 + metadata, resumable uploads, file authz, CDN, scanning |
| 10 | caching-redis | Cache patterns, Redis client hygiene, TTL/eviction, invalidation, stampede/hot keys, locks, rate limiting, Streams, HA |
| 11 | background-processing-messaging | Queues, ARQ vs Celery, retries, idempotent tasks, schedulers, RabbitMQ vs Kafka vs NATS, delivery semantics, DLQ, backpressure, outbox |
| 12 | real-time-communication | WebSockets, SSE, polling, auth, scaling across replicas, fan-out, reconnection, backpressure |
| 13 | testing-backend-systems | Unit/integration/API/contract/DB tests, factories, Testcontainers, async/WS/worker tests, load and failure tests |
| 14 | docker-ci-cd-deployment | Images, Python in a container, Compose, secrets, health checks, Swarm, GitHub Actions, deployment strategies, rollback |
| 15 | observability-reliability | Logs, request IDs, metrics, Prometheus, tracing/OTel, health/readiness, SLOs, alerting, timeouts/retries/breakers/bulkheads, incidents |
| 16 | security | OWASP API Top 10, injection, XSS/CSRF/SSRF, BOLA/BFLA, abuse/DoS, secrets, supply chain, headers, PII, deletion |
| 17 | performance-scalability | Percentiles, profiling a live service, slow-endpoint method, server tuning, scaling, load balancing, replicas, capacity |
| 18 | backend-architecture | Monolith vs modular vs microservices, ports and adapters, DDD, service communication, gateway/BFF, multi-tenancy, EDA, CQRS |
| 19 | distributed-systems | Partial failure, clocks and IDs, CAP, consistency, idempotency end-to-end, 2PC, sagas, event sourcing, replication overview |
| 20 | production-projects | Rate-limited API · Auth service · Event-driven orders · Real-time notifications · NMS-style monitoring backend · reliability lab |

> **Altitude rule.** Some topics appear in more than one track on purpose.
> `modern-python` teaches the *language and its libraries* (DB-API, `sqlite3`,
> SQLAlchemy mechanics). `backend-development` teaches *building one service*
> (schema design, migrations, pooling). A future system-design track teaches
> *how many services behave together* (sharding, replication, consistency).
> Keep new material at the altitude of its track.
