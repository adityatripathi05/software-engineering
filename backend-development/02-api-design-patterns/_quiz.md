# Module 02 — Self-Test

Retrieval practice for [API Design Patterns](README.md). Attempt every question — aloud or on
paper — **before** opening the Answers at the bottom. This module's incidents mostly produced
`2xx` responses while breaking customers, so the questions lean on the failure signatures:
if you can reconstruct the mechanism from the symptom, you own the material.

**How to use these notes:** state your own Mental Model before reading the given one · answer
Interview Questions aloud before the answer shape · type and run one code block per notebook ·
reattempt this quiz a week later.

---

## Questions

1. `response_model` is called a security boundary in this module. What exactly leaks without
   it, through what mechanism — and which *second* artefact turns contract changes into
   reviewable diffs?
2. Two different tenants both send `Idempotency-Key: invoice-001`, and one receives the
   other's invoice. What are the three components of a correctly scoped key, and what extra
   check catches "same key, different payload"?
3. Why does a trailing-slash `307` redirect end in `401 Unauthorized`? Walk the second
   request. Which config rule retires the whole class?
4. Why must you never return `404` for an operation id you just issued? What must be true —
   transactionally — before the handle leaves the building, and what did clients reasonably
   do when it wasn't?
5. Explain, with the concrete insert that causes it, how offset pagination lost 340 invoices
   from a month-end export under `created_at DESC`. What property must a cursor's sort key
   have?
6. A customer's 4,100-invoice job halted because someone edited an error message's wording.
   Whose fault is that, and what should the client have been given to branch on instead?
   Name the RFC and the field.
7. The rate limiter saw 11 requests while the database executed 5,001 statements. State the
   general lesson about your defences in one sentence, then name the two cost controls the
   GraphQL schema lacked.
8. Absent, null, valued: give the Pydantic v2 call that preserves the three-state distinction
   at an update boundary, and say what each state must mean in a PATCH.
9. "Whoever shares a bucket shares a fate." Derive the quota design from that sentence: what
   should determine a request's bucket, and which headers must every `200` carry?
10. Why is adding an enum value a breaking change for a generated Java SDK but harmless for a
    typical Python client? What compatibility posture and what CI job follow from that
    asymmetry?
11. One hanging webhook receiver occupied 187 of 200 delivery workers. Name the pattern that
    prevents it — and the two other places in this module where the same pattern appears
    wearing different clothes.
12. "Every sortable field is a standing index commitment." What two things does the closed
    registry of sortable/filterable fields pin together, and what happened when it didn't
    exist?
13. v1 was removed on the announced date, exactly as promised — and production stopped at
    three customers anyway. What three pieces of evidence gate a *safe* removal?
14. Module 02's transferable detection skill: absolute counts hide contract failures; ratios
    expose them. Give three ratio metrics from this module and the incident each would have
    caught.
15. *Mini coding challenge.* Sketch cursor pagination for `GET /v1/invoices` sorted
    `created_at DESC, id DESC`: what the cursor encodes, the `WHERE` clause it produces, and
    why the tiebreaker column is not optional.
16. *Mini coding challenge.* Sketch the idempotency-key flow on `POST /v1/invoices`: what row
    is written, in what transaction relative to the business write, and what is returned on
    replay — (a) same key + same payload, (b) same key + different payload, (c) key currently
    in flight.
17. "Your generated SDKs have been wrong for months and nobody noticed." Which two incidents
    in this module does that sentence describe, and what single committed artefact addresses
    both?
18. *Design prompt.* A partner needs bulk invoice import (10,000 rows), progress tracking,
    completion webhooks, and fair rate limiting alongside their interactive dashboard.
    Compose the design from 02.7 + 02.10 + 02.11 + 02.12: request shape and partial-success
    reporting, the operation lifecycle and its status codes, delivery isolation, and quota
    classes.

---

## Answers

1. With no declared response type FastAPI serialises whatever the handler returns — every ORM
   attribute, including CRM notes and a churn score, published for seven months (02.4). The
   declared model is the filter; the committed `openapi.json`, regenerated and diffed in CI,
   makes any contract change visible in review.
2. Scope = `(tenant, api_key, key)` — client-supplied identifiers live in the *client's*
   namespace (02.8). Store a request fingerprint with the key; same key + different payload
   is a `422` problem, not a replay.
3. The `307`'s `Location` was built from proxy headers the app didn't receive, naming an
   internal host; the client's second request went cross-origin and dropped `Authorization`
   (02.1). Rule: one canonical URI form, no slash redirects (`redirect_slashes` off), opaque
   prefixed ids.
4. Never hand back a handle to something not yet durably readable (02.10): the operation row
   and the job enqueue must commit in one transaction *before* the id is returned, and the
   status endpoint must read where that write is visible. The replica-lagged `404` told SDKs
   "submission failed" — they resubmitted, 22× the work.
5. Page 1 is read; new invoices are inserted at the top; `OFFSET 100` now skips rows that
   were on page 1's boundary — position-by-counting is only valid if the list never changes
   (02.5). A cursor's sort key must be **totally ordered and stable** (hence the unique
   tiebreaker).
6. Ledgerly's fault: if clients parse `detail`, the API never gave them a stable identity
   (02.9). RFC 9457 Problem Details; the `type` URI is the contract, `detail` is documented
   as mutable prose.
7. Every defence you own is denominated in *requests* — but cost is denominated in work
   (02.2). Missing: a query depth limit and a complexity/cost budget evaluated before
   execution (plus result-size caps).
8. `model_dump(exclude_unset=True)` (02.7). Absent = "don't touch this field"; null =
   "explicitly clear it"; valued = "set it to this". Collapsing absent into null is how a
   one-field PATCH erases three others under `200 OK`.
9. Quota class derives from the *credential type* (interactive session vs API key vs batch
   job), so machines and humans never share a bucket (02.12). Every `200` carries
   `RateLimit-*` headers so clients can pace before the `429`, which carries `Retry-After`.
10. Generated strict-language SDKs compile the enum closed — an unknown value is a
    deserialisation error; dynamic clients shrug (02.3). "Additive" must be judged against
    your strictest consumer: enums open unless deliberately closed, plus a CI job that
    round-trips new schemas through the strictest generated SDK.
11. Per-destination bulkheads (02.11). The same isolation appears as the separate connection
    pool bounding GraphQL blast radius (02.2) and as per-credential quota classes (02.12) —
    module 15 finally names the pattern.
12. The registry pins the public contract (which fields are sortable/filterable) to the
    physical commitment (an index for each) (02.6). Without it, `?sort=notes` reached the
    database as a 2.3 GB disk sort that degraded every tenant.
13. Zero measured usage per client (per-client telemetry, since 0.05% of traffic can be 100%
    of one customer's business), verified *technical* contacts, and brownouts that force
    silent clients to surface before the hard stop (02.13). Enforced in the release pipeline,
    not a calendar.
14. SQL-statements-per-request (catches 02.2); operations-per-idempotency-key or
    resubmissions-per-handle (02.10); worker-share-per-destination (02.11);
    404-rate-on-ids-we-issued (02.10). Any three.
15. Cursor encodes the last row's `(created_at, id)`; `WHERE (created_at, id) <
    (:cursor_ts, :cursor_id) ORDER BY created_at DESC, id DESC LIMIT :n`. Without `id`,
    equal timestamps make the ordering non-total: rows straddling a page boundary repeat or
    vanish.
16. Claim the key row (scoped, with fingerprint and state `in_flight`) via
    `INSERT … ON CONFLICT`, committed *first, on its own* — so concurrent duplicates can see
    it; then the business write and the completion record (stored response, state
    `completed`) commit together in *one* transaction. (a) Return the stored response replay
    with an idempotent-replay marker. (b) `422` problem — key reuse with different payload.
    (c) `409`/retry-later, never a second execution (02.8).
17. 02.4 (undeclared response fields — the SDKs never knew nine fields existed) and 02.3
    (closed enums — SDKs crashed on a value the API considered additive). The committed,
    CI-diffed `openapi.json` is the artefact both fixes hang off.
18. Strong shape: `POST /v1/invoices:bulk` with per-item results (207-style body, absent ≠
    null per 02.7); returns an operation id written transactionally with the enqueue, polled
    at `/v1/operations/{id}` — never `404` for a fresh id (02.10); completion webhook
    delivered through per-destination bulkheaded workers with receiver-side dedupe (02.11);
    batch traffic in its own quota class with `RateLimit-*` feedback so the dashboard never
    starves (02.12).
