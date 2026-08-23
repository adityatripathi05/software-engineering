# Software Engineering

Self-paced engineering notes that are organised into tracks.

| Track | Status | Covers |
|---|---|---|
| [`modern-python/`](modern-python/) | **Complete** — 107 notebooks | The language and its ecosystem, from first principles to four end-to-end builds |
| [`backend-development/`](backend-development/) | **Outline only** — no notebooks yet | Building one service correctly: HTTP, FastAPI, PostgreSQL, auth, caching, Docker, CI/CD |

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

Scaffolded as an outline. No notebooks yet — each folder currently holds only a
`.gitkeep`.

| # | Folder | Planned coverage |
|---|--------|------------------|
| 01 | backend-fundamentals | What a backend is, request lifecycle, processes and ports, the shape of a service |
| 02 | http-and-web | HTTP semantics, headers, status codes, cookies, CORS, content negotiation |
| 03 | rest-api-design | Resources, verbs, versioning, error contracts, idempotency |
| 04 | fastapi | Routing, dependency injection, async endpoints, OpenAPI |
| 05 | pydantic | Models, validators, settings, serialisation boundaries |
| 06 | postgresql | Schema design, indexing, query plans, transactions, connection pooling |
| 07 | sqlalchemy | Core vs ORM, sessions, relationships, unit of work |
| 08 | alembic | Migrations, autogenerate, branching, rollback strategy |
| 09 | authentication-and-authorization | Sessions, JWT, OAuth2, password handling, RBAC |
| 10 | redis-and-caching | Cache patterns, invalidation, TTLs, rate limiting |
| 11 | background-processing | Queues, workers, retries, idempotent jobs, scheduling |
| 12 | api-patterns | Pagination, filtering, bulk operations, webhooks, streaming |
| 13 | backend-testing | Test databases, fixtures, contract tests, integration vs unit |
| 14 | security | OWASP basics, injection, secrets, TLS, input trust boundaries |
| 15 | docker | Images, layers, compose, dev vs prod builds |
| 16 | observability | Structured logging, metrics, tracing, health checks |
| 17 | cicd | Pipelines, test gates, build artefacts, deployment strategies |
| 18 | performance | Profiling a service, N+1 queries, connection limits, load testing |
| 19 | reliability | Timeouts, retries, circuit breakers, graceful degradation, SLOs |

> **Altitude rule.** Some topics appear in more than one track on purpose.
> `modern-python` teaches the *language and its libraries* (DB-API, `sqlite3`,
> SQLAlchemy mechanics). `backend-development` teaches *building one service*
> (schema design, migrations, pooling). A future system-design track teaches
> *how many services behave together* (sharding, replication, consistency).
> Keep new material at the altitude of its track.
