# backend-development - Curriculum & Progress

Generated from `_tools/curriculum.py`. Edit that file (incl. `STATUS`) and run `python backend-development/_tools/build.py` from the repo root.
Legend: `[ ]` todo · `[~]` draft · `[r]` in review · `[x]` done.

Authoring rules for every notebook: [AUTHORING-GUIDE.md](AUTHORING-GUIDE.md). Design rationale: [CURRICULUM-REVIEW.md](CURRICULUM-REVIEW.md).

**Progress: 0/261 notebooks done.**

| # | Module | Notebooks | Done | Prereq (modern-python) | Depends on |
|---|---|---|---|---|---|
| 01 | [HTTP & Web Fundamentals](01-http-web-fundamentals/README.md) | 10 | 0 | modern-python 11.1-11.5 | - |
| 02 | [API Design & Patterns](02-api-design-patterns/README.md) | 13 | 0 | modern-python 18.1, 18.3 | 01 |
| 03 | [FastAPI](03-fastapi/README.md) | 14 | 0 | modern-python 5.4, 12.5, 18.4 | 01, 02 |
| 04 | [Async & Concurrency for Backend](04-async-concurrency/README.md) | 10 | 0 | modern-python 12.1-12.5 | 03 |
| 05 | [PostgreSQL & Data Modeling](05-postgresql-data-modeling/README.md) | 18 | 0 | modern-python 10.1, 10.2, 10.5 | 04 |
| 06 | [SQLAlchemy & Data Access](06-sqlalchemy-data-access/README.md) | 13 | 0 | modern-python 10.4, 6.3 | 03, 04, 05 |
| 07 | [Backend Design Patterns](07-backend-design-patterns/README.md) | 10 | 0 | modern-python 5.4, 16.4 | 03, 06 |
| 08 | [Authentication & Authorization](08-authentication-authorization/README.md) | 17 | 0 | modern-python 18.2 | 03, 06, 07, 10 |
| 09 | [File Handling & Object Storage](09-file-handling-object-storage/README.md) | 8 | 0 | modern-python 8.5 | 03, 08 (forward-ref 11) |
| 10 | [Caching & Redis](10-caching-redis/README.md) | 17 | 0 | modern-python 10.5 | 04, 05 |
| 11 | [Background Processing & Messaging](11-background-processing-messaging/README.md) | 16 | 0 | modern-python 12.3, 12.4 | 04, 05, 06, 10 |
| 12 | [Real-Time Communication](12-real-time-communication/README.md) | 11 | 0 | modern-python 11.4, 12.5 | 03, 04, 08, 10 |
| 13 | [Testing Backend Systems](13-testing-backend-systems/README.md) | 14 | 0 | modern-python 15.3-15.6 | 03-12 |
| 14 | [Docker, CI/CD & Deployment](14-docker-ci-cd-deployment/README.md) | 17 | 0 | modern-python 17.1-17.3 | 03.14, 06.13, 13 |
| 15 | [Observability & Reliability](15-observability-reliability/README.md) | 18 | 0 | modern-python 15.10 | 04.4, 14 |
| 16 | [API & Application Security](16-security/README.md) | 14 | 0 | modern-python 18.2 | 01, 03, 08 |
| 17 | [Performance & Scalability](17-performance-scalability/README.md) | 14 | 0 | modern-python 17.5 | 05, 06, 10, 13.13, 15 |
| 18 | [Backend Architecture](18-backend-architecture/README.md) | 9 | 0 | - | 07, 11, 15 |
| 19 | [Distributed Systems Fundamentals](19-distributed-systems/README.md) | 12 | 0 | modern-python 10.5 | 11, 15, 18 |
| 20 | [Production Backend Projects](20-production-projects/README.md) | 6 | 0 | modern-python 19.3, 19.4 | all |

## 01 HTTP & Web Fundamentals

Folder `01-http-web-fundamentals/` · Prereq: modern-python 11.1-11.5 · Depends on: -

- [r] **01.1** [Request/response lifecycle - socket to ASGI to handler](01-http-web-fundamentals/01.1-request-response-lifecycle.md) - Beginner
- [r] **01.2** [HTTP methods, safety and idempotency](01-http-web-fundamentals/01.2-methods-safety-idempotency.md) - Beginner
- [r] **01.3** [Status codes and headers](01-http-web-fundamentals/01.3-status-codes-and-headers.md) - Beginner
- [r] **01.4** [Content negotiation, compression and HTTP caching - ETag, Cache-Control, conditional requests](01-http-web-fundamentals/01.4-content-negotiation-and-http-caching.md) - Intermediate
- [r] **01.5** [Cookies and sessions](01-http-web-fundamentals/01.5-cookies-and-sessions.md) - Beginner
- [r] **01.6** [Stateless vs stateful services](01-http-web-fundamentals/01.6-stateless-vs-stateful.md) - Beginner
- [r] **01.7** [Connection lifecycle - keep-alive, HTTP/1.1 vs 2 vs 3](01-http-web-fundamentals/01.7-connection-lifecycle.md) - Intermediate
- [r] **01.8** [TLS fundamentals](01-http-web-fundamentals/01.8-tls-fundamentals.md) - Intermediate
- [r] **01.9** [CORS - preflight, browser security model, misconfiguration](01-http-web-fundamentals/01.9-cors.md) - Intermediate
- [r] **01.10** [Reverse proxies and load balancers - X-Forwarded-*, trusting proxy headers](01-http-web-fundamentals/01.10-reverse-proxies-and-forwarded-headers.md) - Intermediate

## 02 API Design & Patterns

Folder `02-api-design-patterns/` · Prereq: modern-python 18.1, 18.3 · Depends on: 01

- [r] **02.1** [Resource modelling and URI design](02-api-design-patterns/02.1-resource-modelling-and-uri-design.md) - Beginner
- [r] **02.2** [REST vs RPC vs GraphQL vs gRPC](02-api-design-patterns/02.2-rest-vs-rpc-vs-graphql-vs-grpc.md) - Intermediate
- [r] **02.3** [API versioning](02-api-design-patterns/02.3-api-versioning.md) - Intermediate
- [r] **02.4** [Contract-first design and OpenAPI](02-api-design-patterns/02.4-contract-first-and-openapi.md) - Intermediate
- [r] **02.5** [Pagination - offset, cursor, keyset](02-api-design-patterns/02.5-pagination.md) - Intermediate
- [r] **02.6** [Filtering, sorting and searching](02-api-design-patterns/02.6-filtering-sorting-searching.md) - Beginner
- [r] **02.7** [Bulk operations and partial updates (PATCH)](02-api-design-patterns/02.7-bulk-operations-and-partial-updates.md) - Intermediate
- [r] **02.8** [Idempotency and idempotency keys](02-api-design-patterns/02.8-idempotency-keys.md) - Intermediate
- [r] **02.9** [Standardised error responses - RFC 9457 Problem Details](02-api-design-patterns/02.9-error-responses-rfc-9457.md) - Beginner
- [r] **02.10** [Long-running operations - 202 + polling vs webhooks vs SSE](02-api-design-patterns/02.10-long-running-operations.md) - Intermediate
- [r] **02.11** [Webhook design - signatures, replay protection, retries, delivery guarantees](02-api-design-patterns/02.11-webhook-design.md) - Advanced
- [r] **02.12** [Rate limiting as an API contract - 429, Retry-After, RateLimit headers](02-api-design-patterns/02.12-rate-limiting-as-api-contract.md) - Intermediate
- [r] **02.13** [API deprecation, compatibility and sunset](02-api-design-patterns/02.13-deprecation-and-sunset.md) - Intermediate

## 03 FastAPI

Folder `03-fastapi/` · Prereq: modern-python 5.4, 12.5, 18.4 · Depends on: 01, 02

- [r] **03.1** [Application structure and ASGI - what uvicorn actually does](03-fastapi/03.1-application-structure-and-asgi.md) - Beginner
- [r] **03.2** [Routing and parameters](03-fastapi/03.2-routing-and-parameters.md) - Beginner
- [r] **03.3** [Request/response models](03-fastapi/03.3-request-response-models.md) - Beginner
- [r] **03.4** [Pydantic v2 in depth - validation modes, serialisation, settings](03-fastapi/03.4-pydantic-v2-in-depth.md) - Intermediate
- [r] **03.5** [Dependency injection](03-fastapi/03.5-dependency-injection.md) - Intermediate
- [r] **03.6** [Sync vs async endpoints - the threadpool](03-fastapi/03.6-sync-vs-async-endpoints.md) - Intermediate
- [r] **03.7** [Middleware](03-fastapi/03.7-middleware.md) - Intermediate
- [r] **03.8** [Exception handling and error mapping](03-fastapi/03.8-exception-handling.md) - Intermediate
- [r] **03.9** [Lifespan and application lifecycle](03-fastapi/03.9-lifespan.md) - Intermediate
- [r] **03.10** [BackgroundTasks vs real workers](03-fastapi/03.10-backgroundtasks-vs-workers.md) - Intermediate
- [r] **03.11** [File uploads and streaming responses](03-fastapi/03.11-file-uploads-and-streaming.md) - Intermediate
- [r] **03.12** [WebSockets basics](03-fastapi/03.12-websockets-basics.md) - Intermediate
- [r] **03.13** [OpenAPI customisation](03-fastapi/03.13-openapi-customisation.md) - Beginner
- [r] **03.14** [Production deployment - uvicorn/gunicorn workers, signals, behind a proxy](03-fastapi/03.14-production-deployment.md) - Advanced

## 04 Async & Concurrency for Backend

Folder `04-async-concurrency/` · Prereq: modern-python 12.1-12.5 · Depends on: 03

- [~] **04.1** [The event loop inside a server process](04-async-concurrency/04.1-event-loop-in-a-server.md) - Intermediate
- [~] **04.2** [Blocking vs non-blocking I/O - finding the blocking call](04-async-concurrency/04.2-blocking-vs-non-blocking-io.md) - Intermediate
- [~] **04.3** [Async database and HTTP clients - pools and limits](04-async-concurrency/04.3-async-db-and-http-clients.md) - Intermediate
- [~] **04.4** [Request-scoped state - contextvars](04-async-concurrency/04.4-request-scoped-state-contextvars.md) - Intermediate
- [ ] **04.5** [Race conditions in concurrent requests - asyncio.Lock and Queue](04-async-concurrency/04.5-race-conditions-in-concurrent-requests.md) - Advanced
- [ ] **04.6** [Lost updates and double writes](04-async-concurrency/04.6-lost-updates-and-double-writes.md) - Advanced
- [ ] **04.7** [CPU-bound work and event-loop blocking](04-async-concurrency/04.7-cpu-bound-work.md) - Intermediate
- [ ] **04.8** [Timeouts and cancellation](04-async-concurrency/04.8-timeouts-and-cancellation.md) - Advanced
- [ ] **04.9** [Graceful shutdown](04-async-concurrency/04.9-graceful-shutdown.md) - Advanced
- [ ] **04.10** [When async helps and when it does not](04-async-concurrency/04.10-when-async-helps.md) - Intermediate

## 05 PostgreSQL & Data Modeling

Folder `05-postgresql-data-modeling/` · Prereq: modern-python 10.1, 10.2, 10.5 · Depends on: 04

- [ ] **05.1** [Relational modelling and key choice - serial, UUIDv4, UUIDv7](05-postgresql-data-modeling/05.1-relational-modelling-and-keys.md) - Beginner
- [ ] **05.2** [Normalisation and denormalisation tradeoffs](05-postgresql-data-modeling/05.2-normalisation-tradeoffs.md) - Intermediate
- [ ] **05.3** [Constraints, data integrity and upsert](05-postgresql-data-modeling/05.3-constraints-integrity-upsert.md) - Intermediate
- [ ] **05.4** [Multi-tenant data modelling](05-postgresql-data-modeling/05.4-multi-tenant-data-modelling.md) - Intermediate
- [ ] **05.5** [Indexing](05-postgresql-data-modeling/05.5-indexing.md) - Intermediate
- [ ] **05.6** [EXPLAIN and EXPLAIN ANALYZE](05-postgresql-data-modeling/05.6-explain-analyze.md) - Intermediate
- [ ] **05.7** [Query optimisation and pg_stat_statements](05-postgresql-data-modeling/05.7-query-optimisation.md) - Advanced
- [ ] **05.8** [Search in Postgres - full-text and pgvector basics](05-postgresql-data-modeling/05.8-full-text-search-and-pgvector.md) - Intermediate
- [ ] **05.9** [Connection pooling and PgBouncer](05-postgresql-data-modeling/05.9-connection-pooling-and-pgbouncer.md) - Intermediate
- [ ] **05.10** [Transactions and ACID](05-postgresql-data-modeling/05.10-transactions-and-acid.md) - Intermediate
- [ ] **05.11** [Isolation levels, MVCC, bloat and vacuum](05-postgresql-data-modeling/05.11-isolation-mvcc-vacuum.md) - Advanced
- [ ] **05.12** [Locks and deadlocks](05-postgresql-data-modeling/05.12-locks-and-deadlocks.md) - Advanced
- [ ] **05.13** [Optimistic vs pessimistic concurrency control](05-postgresql-data-modeling/05.13-optimistic-vs-pessimistic.md) - Advanced
- [ ] **05.14** [SELECT FOR UPDATE and SKIP LOCKED](05-postgresql-data-modeling/05.14-select-for-update-skip-locked.md) - Advanced
- [ ] **05.15** [JSONB](05-postgresql-data-modeling/05.15-jsonb.md) - Intermediate
- [ ] **05.16** [CTEs and window functions](05-postgresql-data-modeling/05.16-ctes-and-window-functions.md) - Intermediate
- [ ] **05.17** [Partitioning](05-postgresql-data-modeling/05.17-partitioning.md) - Advanced
- [ ] **05.18** [Backup, restore, PITR, RTO and RPO](05-postgresql-data-modeling/05.18-backup-restore-pitr.md) - Intermediate

## 06 SQLAlchemy & Data Access

Folder `06-sqlalchemy-data-access/` · Prereq: modern-python 10.4, 6.3 · Depends on: 03, 04, 05

- [ ] **06.1** [Core vs ORM](06-sqlalchemy-data-access/06.1-core-vs-orm.md) - Beginner
- [ ] **06.2** [Engine and connection lifecycle](06-sqlalchemy-data-access/06.2-engine-and-connection-lifecycle.md) - Intermediate
- [ ] **06.3** [Session lifecycle](06-sqlalchemy-data-access/06.3-session-lifecycle.md) - Intermediate
- [ ] **06.4** [Relationships and loading strategies](06-sqlalchemy-data-access/06.4-relationships-and-loading-strategies.md) - Intermediate
- [ ] **06.5** [The N+1 problem](06-sqlalchemy-data-access/06.5-n-plus-one.md) - Intermediate
- [ ] **06.6** [Transactions](06-sqlalchemy-data-access/06.6-transactions.md) - Intermediate
- [ ] **06.7** [Sync vs async SQLAlchemy - psycopg3 vs asyncpg](06-sqlalchemy-data-access/06.7-sync-vs-async-sqlalchemy.md) - Intermediate
- [ ] **06.8** [Connection pool configuration](06-sqlalchemy-data-access/06.8-connection-pool-configuration.md) - Intermediate
- [ ] **06.9** [FastAPI integration](06-sqlalchemy-data-access/06.9-fastapi-integration.md) - Intermediate
- [ ] **06.10** [Repository and Unit of Work](06-sqlalchemy-data-access/06.10-repository-and-unit-of-work.md) - Advanced
- [ ] **06.11** [Bulk operations and raw-SQL escape hatches](06-sqlalchemy-data-access/06.11-bulk-operations-and-raw-sql.md) - Intermediate
- [ ] **06.12** [Alembic migrations](06-sqlalchemy-data-access/06.12-alembic-migrations.md) - Intermediate
- [ ] **06.13** [Zero-downtime and backward-compatible migrations](06-sqlalchemy-data-access/06.13-zero-downtime-migrations.md) - Advanced

## 07 Backend Design Patterns

Folder `07-backend-design-patterns/` · Prereq: modern-python 5.4, 16.4 · Depends on: 03, 06

- [ ] **07.1** [Layered architecture](07-backend-design-patterns/07.1-layered-architecture.md) - Beginner
- [ ] **07.2** [Router/controller layer](07-backend-design-patterns/07.2-router-controller-layer.md) - Beginner
- [ ] **07.3** [Service layer and mapping domain errors to HTTP](07-backend-design-patterns/07.3-service-layer.md) - Intermediate
- [ ] **07.4** [Repository pattern](07-backend-design-patterns/07.4-repository-pattern.md) - Intermediate
- [ ] **07.5** [Unit of Work](07-backend-design-patterns/07.5-unit-of-work.md) - Intermediate
- [ ] **07.6** [DTO/API schema vs domain model vs persistence model](07-backend-design-patterns/07.6-dto-vs-domain-vs-persistence.md) - Intermediate
- [ ] **07.7** [Dependency Injection as a general pattern](07-backend-design-patterns/07.7-dependency-injection-as-a-pattern.md) - Intermediate
- [ ] **07.8** [Strategy and Factory patterns](07-backend-design-patterns/07.8-strategy-and-factory.md) - Intermediate
- [ ] **07.9** [Configuration management - pydantic-settings, 12-factor](07-backend-design-patterns/07.9-configuration-management.md) - Beginner
- [ ] **07.10** [When abstraction becomes harmful](07-backend-design-patterns/07.10-when-abstraction-becomes-harmful.md) - Intermediate

## 08 Authentication & Authorization

Folder `08-authentication-authorization/` · Prereq: modern-python 18.2 · Depends on: 03, 06, 07, 10

- [ ] **08.1** [Sessions vs tokens](08-authentication-authorization/08.1-sessions-vs-tokens.md) - Beginner
- [ ] **08.2** [Cookie security - SameSite, Secure, HttpOnly, session fixation](08-authentication-authorization/08.2-cookie-security.md) - Intermediate
- [ ] **08.3** [JWT architecture and pitfalls](08-authentication-authorization/08.3-jwt-architecture-and-pitfalls.md) - Intermediate
- [ ] **08.4** [Access and refresh tokens](08-authentication-authorization/08.4-access-and-refresh-tokens.md) - Intermediate
- [ ] **08.5** [Refresh-token rotation](08-authentication-authorization/08.5-refresh-token-rotation.md) - Advanced
- [ ] **08.6** [Logout, revocation and denylists](08-authentication-authorization/08.6-logout-revocation-denylists.md) - Intermediate
- [ ] **08.7** [OAuth2](08-authentication-authorization/08.7-oauth2.md) - Intermediate
- [ ] **08.8** [Authorization Code + PKCE](08-authentication-authorization/08.8-authorization-code-pkce.md) - Advanced
- [ ] **08.9** [Client Credentials](08-authentication-authorization/08.9-client-credentials.md) - Intermediate
- [ ] **08.10** [OpenID Connect overview](08-authentication-authorization/08.10-oidc-overview.md) - Intermediate
- [ ] **08.11** [API keys and machine-to-machine auth](08-authentication-authorization/08.11-api-keys-and-m2m.md) - Intermediate
- [ ] **08.12** [RBAC](08-authentication-authorization/08.12-rbac.md) - Intermediate
- [ ] **08.13** [ABAC](08-authentication-authorization/08.13-abac.md) - Advanced
- [ ] **08.14** [Resource ownership](08-authentication-authorization/08.14-resource-ownership.md) - Intermediate
- [ ] **08.15** [Password hashing](08-authentication-authorization/08.15-password-hashing.md) - Intermediate
- [ ] **08.16** [Account flows - password reset, email verification, MFA overview](08-authentication-authorization/08.16-account-flows.md) - Intermediate
- [ ] **08.17** [Credential stuffing, token replay and theft](08-authentication-authorization/08.17-credential-stuffing-replay-theft.md) - Advanced

## 09 File Handling & Object Storage

Folder `09-file-handling-object-storage/` · Prereq: modern-python 8.5 · Depends on: 03, 08 (forward-ref 11)

- [ ] **09.1** [Upload architectures](09-file-handling-object-storage/09.1-upload-architectures.md) - Beginner
- [ ] **09.2** [Direct-to-storage with presigned URLs](09-file-handling-object-storage/09.2-presigned-urls.md) - Intermediate
- [ ] **09.3** [Proxy-through-backend](09-file-handling-object-storage/09.3-proxy-through-backend.md) - Intermediate
- [ ] **09.4** [S3-compatible object storage + metadata in PostgreSQL](09-file-handling-object-storage/09.4-s3-storage-and-postgres-metadata.md) - Intermediate
- [ ] **09.5** [Large, multipart and resumable uploads](09-file-handling-object-storage/09.5-large-multipart-resumable-uploads.md) - Intermediate
- [ ] **09.6** [File authorization and expiring links](09-file-handling-object-storage/09.6-file-authorization-and-expiring-links.md) - Intermediate
- [ ] **09.7** [CDN basics](09-file-handling-object-storage/09.7-cdn-basics.md) - Intermediate
- [ ] **09.8** [Scanning and processing pipelines](09-file-handling-object-storage/09.8-scanning-and-processing-pipelines.md) - Intermediate

## 10 Caching & Redis

Folder `10-caching-redis/` · Prereq: modern-python 10.5 · Depends on: 04, 05

- [ ] **10.1** [Why caching exists - local vs distributed](10-caching-redis/10.1-why-caching.md) - Beginner
- [ ] **10.2** [Cache-aside](10-caching-redis/10.2-cache-aside.md) - Intermediate
- [ ] **10.3** [Write-through](10-caching-redis/10.3-write-through.md) - Intermediate
- [ ] **10.4** [Write-behind](10-caching-redis/10.4-write-behind.md) - Advanced
- [ ] **10.5** [Redis data structures](10-caching-redis/10.5-redis-data-structures.md) - Beginner
- [ ] **10.6** [Redis client in production - pools, timeouts, pipelining](10-caching-redis/10.6-redis-client-in-production.md) - Intermediate
- [ ] **10.7** [TTL and eviction](10-caching-redis/10.7-ttl-and-eviction.md) - Intermediate
- [ ] **10.8** [Cache invalidation](10-caching-redis/10.8-cache-invalidation.md) - Advanced
- [ ] **10.9** [Cache stampede, thundering herd and avalanche](10-caching-redis/10.9-stampede-thundering-herd-avalanche.md) - Advanced
- [ ] **10.10** [Cache penetration](10-caching-redis/10.10-cache-penetration.md) - Intermediate
- [ ] **10.11** [Hot keys](10-caching-redis/10.11-hot-keys.md) - Advanced
- [ ] **10.12** [Distributed locks](10-caching-redis/10.12-distributed-locks.md) - Advanced
- [ ] **10.13** [Rate-limiting algorithms with Redis](10-caching-redis/10.13-rate-limiting-algorithms.md) - Intermediate
- [ ] **10.14** [Sessions in Redis](10-caching-redis/10.14-sessions-in-redis.md) - Intermediate
- [ ] **10.15** [Pub/Sub vs Streams](10-caching-redis/10.15-pubsub-vs-streams.md) - Intermediate
- [ ] **10.16** [Redis persistence](10-caching-redis/10.16-persistence.md) - Intermediate
- [ ] **10.17** [Sentinel and Cluster concepts](10-caching-redis/10.17-sentinel-and-cluster.md) - Intermediate

## 11 Background Processing & Messaging

Folder `11-background-processing-messaging/` · Prereq: modern-python 12.3, 12.4 · Depends on: 04, 05, 06, 10

- [ ] **11.1** [Why background processing exists](11-background-processing-messaging/11.1-why-background-processing.md) - Beginner
- [ ] **11.2** [Request timeout budgets](11-background-processing-messaging/11.2-request-timeout-budgets.md) - Intermediate
- [ ] **11.3** [Job queues](11-background-processing-messaging/11.3-job-queues.md) - Beginner
- [ ] **11.4** [ARQ vs Celery](11-background-processing-messaging/11.4-arq-vs-celery.md) - Intermediate
- [ ] **11.5** [Worker pools](11-background-processing-messaging/11.5-worker-pools.md) - Intermediate
- [ ] **11.6** [Retries and exponential backoff](11-background-processing-messaging/11.6-retries-and-backoff.md) - Intermediate
- [ ] **11.7** [Idempotent task design and idempotent consumers](11-background-processing-messaging/11.7-idempotent-tasks-and-consumers.md) - Advanced
- [ ] **11.8** [Scheduled and periodic jobs](11-background-processing-messaging/11.8-scheduled-and-periodic-jobs.md) - Intermediate
- [ ] **11.9** [Queue vs Pub/Sub vs Streaming](11-background-processing-messaging/11.9-queue-vs-pubsub-vs-streaming.md) - Intermediate
- [ ] **11.10** [RabbitMQ vs Kafka vs NATS](11-background-processing-messaging/11.10-rabbitmq-vs-kafka-vs-nats.md) - Intermediate
- [ ] **11.11** [Delivery semantics - at-most-once, at-least-once, exactly-once](11-background-processing-messaging/11.11-delivery-semantics.md) - Advanced
- [ ] **11.12** [Poison messages and dead-letter queues](11-background-processing-messaging/11.12-poison-messages-and-dlq.md) - Intermediate
- [ ] **11.13** [Consumer lag](11-background-processing-messaging/11.13-consumer-lag.md) - Intermediate
- [ ] **11.14** [Backpressure](11-background-processing-messaging/11.14-backpressure.md) - Advanced
- [ ] **11.15** [Outbox pattern](11-background-processing-messaging/11.15-outbox-pattern.md) - Advanced
- [ ] **11.16** [Job status and results](11-background-processing-messaging/11.16-job-status-and-results.md) - Intermediate

## 12 Real-Time Communication

Folder `12-real-time-communication/` · Prereq: modern-python 11.4, 12.5 · Depends on: 03, 04, 08, 10

- [ ] **12.1** [WebSocket architecture](12-real-time-communication/12.1-websocket-architecture.md) - Intermediate
- [ ] **12.2** [Connection lifecycle](12-real-time-communication/12.2-connection-lifecycle.md) - Intermediate
- [ ] **12.3** [Authentication over WebSockets](12-real-time-communication/12.3-authentication-over-websockets.md) - Intermediate
- [ ] **12.4** [Server-Sent Events](12-real-time-communication/12.4-sse.md) - Intermediate
- [ ] **12.5** [Long polling](12-real-time-communication/12.5-long-polling.md) - Beginner
- [ ] **12.6** [WebSocket vs SSE vs polling](12-real-time-communication/12.6-websocket-vs-sse-vs-polling.md) - Intermediate
- [ ] **12.7** [Scaling WebSockets across replicas](12-real-time-communication/12.7-scaling-across-replicas.md) - Advanced
- [ ] **12.8** [Redis Pub/Sub fan-out](12-real-time-communication/12.8-redis-pubsub-fan-out.md) - Intermediate
- [ ] **12.9** [Reconnection strategy](12-real-time-communication/12.9-reconnection-strategy.md) - Intermediate
- [ ] **12.10** [Backpressure](12-real-time-communication/12.10-backpressure.md) - Advanced
- [ ] **12.11** [Connection limits](12-real-time-communication/12.11-connection-limits.md) - Intermediate

## 13 Testing Backend Systems

Folder `13-testing-backend-systems/` · Prereq: modern-python 15.3-15.6 · Depends on: 03-12

- [ ] **13.1** [Unit testing a service layer](13-testing-backend-systems/13.1-unit-testing-a-service-layer.md) - Beginner
- [ ] **13.2** [Integration testing](13-testing-backend-systems/13.2-integration-testing.md) - Intermediate
- [ ] **13.3** [API testing](13-testing-backend-systems/13.3-api-testing.md) - Intermediate
- [ ] **13.4** [Contract testing and OpenAPI snapshots](13-testing-backend-systems/13.4-contract-testing.md) - Intermediate
- [ ] **13.5** [Database and migration testing](13-testing-backend-systems/13.5-database-and-migration-testing.md) - Intermediate
- [ ] **13.6** [Test isolation and test-data factories](13-testing-backend-systems/13.6-isolation-and-test-data-factories.md) - Intermediate
- [ ] **13.7** [Mocking external services](13-testing-backend-systems/13.7-mocking-external-services.md) - Intermediate
- [ ] **13.8** [Dependency overrides](13-testing-backend-systems/13.8-dependency-overrides.md) - Beginner
- [ ] **13.9** [Async testing](13-testing-backend-systems/13.9-async-testing.md) - Intermediate
- [ ] **13.10** [WebSocket testing](13-testing-backend-systems/13.10-websocket-testing.md) - Intermediate
- [ ] **13.11** [Background-task testing](13-testing-backend-systems/13.11-background-task-testing.md) - Intermediate
- [ ] **13.12** [Testcontainers](13-testing-backend-systems/13.12-testcontainers.md) - Intermediate
- [ ] **13.13** [Load testing with Locust and k6](13-testing-backend-systems/13.13-load-testing.md) - Intermediate
- [ ] **13.14** [Testing failure scenarios](13-testing-backend-systems/13.14-testing-failure-scenarios.md) - Advanced

## 14 Docker, CI/CD & Deployment

Folder `14-docker-ci-cd-deployment/` · Prereq: modern-python 17.1-17.3 · Depends on: 03.14, 06.13, 13

- [ ] **14.1** [Docker fundamentals](14-docker-ci-cd-deployment/14.1-docker-fundamentals.md) - Beginner
- [ ] **14.2** [Image layers](14-docker-ci-cd-deployment/14.2-image-layers.md) - Beginner
- [ ] **14.3** [Multi-stage builds](14-docker-ci-cd-deployment/14.3-multi-stage-builds.md) - Intermediate
- [ ] **14.4** [Python in a container - PID 1, signals, non-root, workers](14-docker-ci-cd-deployment/14.4-python-in-a-container.md) - Intermediate
- [ ] **14.5** [Docker Compose](14-docker-ci-cd-deployment/14.5-docker-compose.md) - Beginner
- [ ] **14.6** [Networking and volumes](14-docker-ci-cd-deployment/14.6-networking-and-volumes.md) - Beginner
- [ ] **14.7** [Environment variables and secrets](14-docker-ci-cd-deployment/14.7-env-vars-and-secrets.md) - Intermediate
- [ ] **14.8** [Health checks](14-docker-ci-cd-deployment/14.8-health-checks.md) - Intermediate
- [ ] **14.9** [Docker Swarm - services, stacks, secrets, rolling updates](14-docker-ci-cd-deployment/14.9-docker-swarm.md) - Intermediate
- [ ] **14.10** [GitHub Actions](14-docker-ci-cd-deployment/14.10-github-actions.md) - Beginner
- [ ] **14.11** [Build / test / security pipeline](14-docker-ci-cd-deployment/14.11-build-test-scan-pipeline.md) - Intermediate
- [ ] **14.12** [Migrations in the deploy pipeline](14-docker-ci-cd-deployment/14.12-migrations-in-the-pipeline.md) - Intermediate
- [ ] **14.13** [Blue-green deployments](14-docker-ci-cd-deployment/14.13-blue-green-deployments.md) - Intermediate
- [ ] **14.14** [Canary deployments](14-docker-ci-cd-deployment/14.14-canary-deployments.md) - Intermediate
- [ ] **14.15** [Rolling deployments](14-docker-ci-cd-deployment/14.15-rolling-deployments.md) - Intermediate
- [ ] **14.16** [Feature flags](14-docker-ci-cd-deployment/14.16-feature-flags.md) - Intermediate
- [ ] **14.17** [Zero-downtime deployment and rollback](14-docker-ci-cd-deployment/14.17-zero-downtime-and-rollback.md) - Advanced

## 15 Observability & Reliability

Folder `15-observability-reliability/` · Prereq: modern-python 15.10 · Depends on: 04.4, 14

- [ ] **15.1** [Structured logging in a service](15-observability-reliability/15.1-structured-logging.md) - Intermediate
- [ ] **15.2** [Correlation and request IDs](15-observability-reliability/15.2-correlation-and-request-ids.md) - Intermediate
- [ ] **15.3** [Metrics](15-observability-reliability/15.3-metrics.md) - Intermediate
- [ ] **15.4** [RED and USE methods](15-observability-reliability/15.4-red-and-use.md) - Intermediate
- [ ] **15.5** [Prometheus](15-observability-reliability/15.5-prometheus.md) - Intermediate
- [ ] **15.6** [Distributed tracing](15-observability-reliability/15.6-distributed-tracing.md) - Intermediate
- [ ] **15.7** [OpenTelemetry](15-observability-reliability/15.7-opentelemetry.md) - Intermediate
- [ ] **15.8** [Health checks](15-observability-reliability/15.8-health-checks.md) - Beginner
- [ ] **15.9** [Liveness vs readiness](15-observability-reliability/15.9-liveness-vs-readiness.md) - Intermediate
- [ ] **15.10** [SLI, SLO and SLA](15-observability-reliability/15.10-sli-slo-sla.md) - Intermediate
- [ ] **15.11** [Alerting](15-observability-reliability/15.11-alerting.md) - Intermediate
- [ ] **15.12** [Alert fatigue](15-observability-reliability/15.12-alert-fatigue.md) - Intermediate
- [ ] **15.13** [Timeouts](15-observability-reliability/15.13-timeouts.md) - Intermediate
- [ ] **15.14** [Retries, backoff and jitter](15-observability-reliability/15.14-retries-backoff-jitter.md) - Intermediate
- [ ] **15.15** [Circuit breakers](15-observability-reliability/15.15-circuit-breakers.md) - Advanced
- [ ] **15.16** [Graceful degradation](15-observability-reliability/15.16-graceful-degradation.md) - Advanced
- [ ] **15.17** [Bulkheads, load shedding and failure isolation](15-observability-reliability/15.17-bulkheads-load-shedding-isolation.md) - Advanced
- [ ] **15.18** [Incident response, runbooks and postmortems](15-observability-reliability/15.18-incident-response-and-postmortems.md) - Intermediate

## 16 API & Application Security

Folder `16-security/` · Prereq: modern-python 18.2 · Depends on: 01, 03, 08

- [ ] **16.1** [OWASP API Security Top 10](16-security/16.1-owasp-api-top-10.md) - Beginner
- [ ] **16.2** [Injection attacks](16-security/16.2-injection.md) - Intermediate
- [ ] **16.3** [Input validation and mass assignment](16-security/16.3-input-validation-and-mass-assignment.md) - Intermediate
- [ ] **16.4** [XSS](16-security/16.4-xss.md) - Intermediate
- [ ] **16.5** [CSRF](16-security/16.5-csrf.md) - Intermediate
- [ ] **16.6** [SSRF](16-security/16.6-ssrf.md) - Intermediate
- [ ] **16.7** [Authentication vulnerabilities](16-security/16.7-authentication-vulnerabilities.md) - Intermediate
- [ ] **16.8** [Authorization vulnerabilities - BOLA and BFLA](16-security/16.8-authorization-vulnerabilities-bola-bfla.md) - Advanced
- [ ] **16.9** [Abuse prevention and DoS hygiene](16-security/16.9-abuse-prevention-and-dos.md) - Intermediate
- [ ] **16.10** [Secrets management](16-security/16.10-secrets-management.md) - Intermediate
- [ ] **16.11** [Dependency and supply-chain security](16-security/16.11-dependency-and-supply-chain.md) - Intermediate
- [ ] **16.12** [Secure headers, including CORS hardening](16-security/16.12-secure-headers.md) - Intermediate
- [ ] **16.13** [PII handling and audit logging](16-security/16.13-pii-and-audit-logging.md) - Intermediate
- [ ] **16.14** [Data deletion and privacy considerations](16-security/16.14-data-deletion-and-privacy.md) - Intermediate

## 17 Performance & Scalability

Folder `17-performance-scalability/` · Prereq: modern-python 17.5 · Depends on: 05, 06, 10, 13.13, 15

- [ ] **17.1** [Performance fundamentals - latency, throughput, percentiles](17-performance-scalability/17.1-performance-fundamentals.md) - Beginner
- [ ] **17.2** [CPU-bound vs I/O-bound workloads](17-performance-scalability/17.2-cpu-bound-vs-io-bound.md) - Intermediate
- [ ] **17.3** [Profiling a running service](17-performance-scalability/17.3-profiling-a-running-service.md) - Intermediate
- [ ] **17.4** [Benchmarking](17-performance-scalability/17.4-benchmarking.md) - Intermediate
- [ ] **17.5** [Slow-endpoint diagnosis - the method](17-performance-scalability/17.5-slow-endpoint-diagnosis.md) - Advanced
- [ ] **17.6** [Data-layer checklist - queries, pool, N+1, pagination, caching revisited](17-performance-scalability/17.6-data-layer-checklist.md) - Intermediate
- [ ] **17.7** [Python server tuning - workers, uvloop, orjson, GC, memory leaks](17-performance-scalability/17.7-python-server-tuning.md) - Advanced
- [ ] **17.8** [Batch processing](17-performance-scalability/17.8-batch-processing.md) - Intermediate
- [ ] **17.9** [Vertical vs horizontal scaling](17-performance-scalability/17.9-vertical-vs-horizontal-scaling.md) - Beginner
- [ ] **17.10** [Stateless services](17-performance-scalability/17.10-stateless-services.md) - Intermediate
- [ ] **17.11** [Load balancing](17-performance-scalability/17.11-load-balancing.md) - Intermediate
- [ ] **17.12** [Read replicas and replica lag](17-performance-scalability/17.12-read-replicas-and-replica-lag.md) - Advanced
- [ ] **17.13** [Sharding - what changes in your code](17-performance-scalability/17.13-sharding-what-changes-in-your-code.md) - Intermediate
- [ ] **17.14** [Capacity planning from load tests](17-performance-scalability/17.14-capacity-planning-from-load-tests.md) - Intermediate

## 18 Backend Architecture

Folder `18-backend-architecture/` · Prereq: - · Depends on: 07, 11, 15

- [ ] **18.1** [Monolith vs modular monolith vs microservices - with a FastAPI modular layout](18-backend-architecture/18.1-monolith-modular-monolith-microservices.md) - Intermediate
- [ ] **18.2** [When NOT to use microservices](18-backend-architecture/18.2-when-not-to-use-microservices.md) - Intermediate
- [ ] **18.3** [Clean and Hexagonal architecture - ports and adapters](18-backend-architecture/18.3-clean-and-hexagonal.md) - Advanced
- [ ] **18.4** [Domain-Driven Design overview](18-backend-architecture/18.4-ddd-overview.md) - Advanced
- [ ] **18.5** [Service communication - sync vs async](18-backend-architecture/18.5-service-communication.md) - Intermediate
- [ ] **18.6** [API Gateway and BFF](18-backend-architecture/18.6-api-gateway-and-bff.md) - Intermediate
- [ ] **18.7** [Multi-tenancy architectures](18-backend-architecture/18.7-multi-tenancy-architectures.md) - Advanced
- [ ] **18.8** [Event-driven architecture](18-backend-architecture/18.8-event-driven-architecture.md) - Advanced
- [ ] **18.9** [CQRS as separate read models](18-backend-architecture/18.9-cqrs.md) - Advanced

## 19 Distributed Systems Fundamentals

Folder `19-distributed-systems/` · Prereq: modern-python 10.5 · Depends on: 11, 15, 18

- [ ] **19.1** [Why distributed systems are hard](19-distributed-systems/19.1-why-distributed-systems-are-hard.md) - Beginner
- [ ] **19.2** [Network failures](19-distributed-systems/19.2-network-failures.md) - Intermediate
- [ ] **19.3** [Timeouts and partial failure](19-distributed-systems/19.3-timeouts-and-partial-failure.md) - Intermediate
- [ ] **19.4** [Clocks, ordering and IDs](19-distributed-systems/19.4-clocks-ordering-and-ids.md) - Intermediate
- [ ] **19.5** [CAP theorem in practice](19-distributed-systems/19.5-cap-in-practice.md) - Intermediate
- [ ] **19.6** [Consistency models](19-distributed-systems/19.6-consistency-models.md) - Advanced
- [ ] **19.7** [Eventual consistency](19-distributed-systems/19.7-eventual-consistency.md) - Intermediate
- [ ] **19.8** [Idempotency and deduplication end-to-end](19-distributed-systems/19.8-idempotency-and-deduplication.md) - Advanced
- [ ] **19.9** [Distributed transactions and 2PC](19-distributed-systems/19.9-distributed-transactions-and-2pc.md) - Advanced
- [ ] **19.10** [Saga pattern](19-distributed-systems/19.10-saga-pattern.md) - Advanced
- [ ] **19.11** [Event sourcing fundamentals](19-distributed-systems/19.11-event-sourcing-fundamentals.md) - Advanced
- [ ] **19.12** [Replication, leaders and consensus - what a backend engineer needs](19-distributed-systems/19.12-replication-leaders-consensus.md) - Advanced

## 20 Production Backend Projects

Folder `20-production-projects/` · Prereq: modern-python 19.3, 19.4 · Depends on: all

- [ ] **20.1** [Project 1 - Rate-limited public API](20-production-projects/20.1-rate-limited-public-api.md) - Intermediate
- [ ] **20.2** [Project 2 - Authentication service](20-production-projects/20.2-authentication-service.md) - Intermediate
- [ ] **20.3** [Project 3 - Event-driven order system](20-production-projects/20.3-event-driven-order-system.md) - Advanced
- [ ] **20.4** [Project 4 - Real-time notification system](20-production-projects/20.4-real-time-notification-system.md) - Advanced
- [ ] **20.5** [Project 5 - NMS-style monitoring backend](20-production-projects/20.5-nms-monitoring-backend.md) - Advanced
- [ ] **20.6** [Optional - Reliability lab: multi-service with tracing, retries, circuit breakers](20-production-projects/20.6-reliability-lab.md) - Advanced
