# 02 API Design & Patterns

Prerequisites: modern-python 18.1, 18.3 · Depends on backend modules: 01

Read top to bottom. Every notebook follows [AUTHORING-GUIDE.md](../AUTHORING-GUIDE.md).

| # | Notebook | Level | Status |
|---|---|---|---|
| 02.1 | [Resource modelling and URI design](02.1-resource-modelling-and-uri-design.md) | Beginner | done |
| 02.2 | [REST vs RPC vs GraphQL vs gRPC](02.2-rest-vs-rpc-vs-graphql-vs-grpc.md) | Intermediate | done |
| 02.3 | [API versioning](02.3-api-versioning.md) | Intermediate | done |
| 02.4 | [Contract-first design and OpenAPI](02.4-contract-first-and-openapi.md) | Intermediate | done |
| 02.5 | [Pagination - offset, cursor, keyset](02.5-pagination.md) | Intermediate | done |
| 02.6 | [Filtering, sorting and searching](02.6-filtering-sorting-searching.md) | Beginner | done |
| 02.7 | [Bulk operations and partial updates (PATCH)](02.7-bulk-operations-and-partial-updates.md) | Intermediate | done |
| 02.8 | [Idempotency and idempotency keys](02.8-idempotency-keys.md) | Intermediate | done |
| 02.9 | [Standardised error responses - RFC 9457 Problem Details](02.9-error-responses-rfc-9457.md) | Beginner | done |
| 02.10 | [Long-running operations - 202 + polling vs webhooks vs SSE](02.10-long-running-operations.md) | Intermediate | done |
| 02.11 | [Webhook design - signatures, replay protection, retries, delivery guarantees](02.11-webhook-design.md) | Advanced | done |
| 02.12 | [Rate limiting as an API contract - 429, Retry-After, RateLimit headers](02.12-rate-limiting-as-api-contract.md) | Intermediate | done |
| 02.13 | [API deprecation, compatibility and sunset](02.13-deprecation-and-sunset.md) | Intermediate | done |

Self-test: [_quiz.md](_quiz.md) - attempt every question before opening the answers at the bottom.

Lab: [_lab/](_lab/) - runnable scripts that reproduce the notebooks' captured transcripts.

---

## Module recap

**Running system:** Ledgerly, continued from module 01 — the invoicing API, its dashboard, its
customer integrations, and now its SDKs, webhooks and versioned contract. Module 03 builds the same
API in FastAPI properly.

**What this module built up.** Module 01 was about the transport: what HTTP does and how each layer
fails. Module 02 is about the **contract** — the promises your API makes and what happens when they
are broken. Its through-line is that an API's hardest problems are not in the happy path but at the
edges of the agreement: what a client may retry, what a client may cache, what "additive" means, what
a partial success is, and how you take something away.

**The incidents, and what each one taught.**

| # | Incident | The general lesson |
|---|---|---|
| 02.1 | A trailing-slash `307` names an internal host; clients drop `Authorization` and get `401` | A redirect is a second request whose target your app computes from proxy headers |
| 02.2 | One GraphQL query issues 5,001 SQL statements; the rate limiter sees 11 requests | Every defence you own is denominated in *requests* |
| 02.3 | A new enum value breaks every generated Java and Go SDK; Python clients are fine | "Additive" must be judged against your **strictest** consumer |
| 02.4 | A missing `response_model` publishes CRM notes and a churn score for seven months | `response_model` is a security boundary; without it, migrations change your public API |
| 02.5 | Offset pagination silently drops 340 invoices from a month-end export | Position by counting is only valid if the list never changes |
| 02.6 | `?sort=notes` becomes a 2.3 GB disk sort that degrades every tenant | Every sortable field is a standing index commitment |
| 02.7 | A one-field `PATCH` erases three others; every response is `200 OK` | Absent, null and valued are **three** states, not two |
| 02.8 | Two tenants use `Idempotency-Key: invoice-001`; one receives the other's invoice | Client-supplied identifiers live in the client's namespace |
| 02.9 | A copy edit to an error message halts a customer's 4,100-invoice job | If clients parse `detail`, you never gave them a stable `type` |
| 02.10 | A replica-lagged status endpoint `404`s a fresh job handle; clients resubmit 22× the work | Never hand back a handle to something not yet durably readable |
| 02.11 | One hanging webhook receiver occupies 187 of 200 delivery workers | A shared pool across destinations you do not control is head-of-line blocking |
| 02.12 | An overnight sync exhausts the tenant quota; twelve humans are locked out at month-end | Whoever shares a bucket shares a fate |
| 02.13 | v1 removed on the announced date; 0.05% of traffic was one customer's whole pipeline | You cannot remove what you cannot measure |

**The pattern across all thirteen.** Module 01's recurring lesson was that healthy-looking systems
can be badly wrong. Module 02 sharpens it: **contract violations produce no server-side signal at
all.** In 02.3, 02.4, 02.5, 02.7, 02.8 and 02.9 the API returned `2xx` for every request while
leaking data, destroying fields, losing rows or breaking integrations. The detection mechanisms that
actually worked were, in order of frequency:

1. A customer noticed.
2. Traffic for one client quietly stopped (02.3, 02.9 — and 01.4, 01.8 before them).
3. A ratio went wrong that nobody was watching: SQL-per-request (02.2), operations-per-idempotency-key
   (02.10), worker-share-per-destination (02.11), `404`-rate-on-ids-we-issued (02.10).

That third category is the transferable skill. Absolute counts hide these failures; **ratios between
two things that should track each other** expose them.

**Contract rules established here** (each asserted by a CI test in its notebook):

```text
one canonical URI form; no slash redirects; opaque prefixed ids       (02.1)
any client-controlled cost needs a cost model before release          (02.2)
enums open unless deliberately closed; strict-SDK compat job in CI    (02.3)
every route declares a filtered response type; openapi.json committed (02.4)
cursor pagination by default; sort keys totally ordered               (02.5)
closed registry for sortable/filterable fields, each with an index    (02.6)
model_dump(exclude_unset=True) at every update boundary               (02.7)
idempotency keys scoped (tenant, api_key, key) + request fingerprint  (02.8)
stable `type` URI per error; `detail` documented as mutable prose     (02.9)
operation row + job enqueue in one transaction; never 404 a fresh id  (02.10)
per-destination bulkheads on all outbound delivery                    (02.11)
quota classes derived from credential type; RateLimit-* on every 200  (02.12)
removal gated on zero usage, enforced in the release pipeline         (02.13)
```

**Recurring cross-cutting threads picked up here.** *Idempotency* appears in 02.7 (per item), 02.8
(the full mechanism), 02.10 (per submission) and 02.11 (receivers must dedupe) — and closes in 19.8.
*Bulkheads* appear in 02.2 (a separate connection pool), 02.11 (per-destination workers) and 02.12
(quota classes), all before module 15 names the pattern. *The outbox* is required by 02.10 and 02.11
and is built in 11.15.

**What module 03 assumes.** That you can specify an endpoint before writing it: method, status,
headers, response model, error types, pagination style, idempotency requirement and rate-limit class.
Module 03 is about making FastAPI express that specification faithfully — and about the framework
mechanics (dependency injection, middleware ordering, lifespan, the sync/async threadpool) that
decide whether it does.
