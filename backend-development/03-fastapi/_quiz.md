# Module 03 — Self-Test

Retrieval practice for [FastAPI](README.md). Attempt every question — aloud or on paper —
**before** opening the Answers at the bottom. Most of this module's incidents came from the
framework doing *exactly what it was told*; the questions test whether you know what it was
told. (03.14 questions will be added when that notebook lands.)

**How to use these notes:** state your own Mental Model before reading the given one · answer
Interview Questions aloud before the answer shape · type and run one code block per notebook ·
reattempt this quiz a week later.

---

## Questions

1. A middleware ships with the review comment "added last so nothing escapes it" — and the
   dashboard is down six minutes later. State the `add_middleware` ordering rule, explain
   what killed the preflights specifically, and why no exception handler saved them.
2. Why must the SQLAlchemy engine be created in lifespan rather than at import time? Give the
   two distinct failure classes import-time creation produces.
3. A customer holds a `201 Created` for an invoice that does not exist. When does dependency
   teardown code after `yield` run relative to the response — and what does that timing
   forbid you from putting there?
4. Why does an unhandled exception on an *accepted* WebSocket produce a retry storm, when the
   same bug over HTTP produces a quiet 500? Name the close code the client reports, and say
   who actually "sends" it.
5. 1,847 invoices reconciled wrong with zero errors raised. What is the models-per-direction
   rule, and which exception protects the *output* direction when a handler violates its own
   contract?
6. State the lifespan doctrine in one sentence, then explain why `redis.ping()` violated it
   while raising on a malformed `DATABASE_URL` does not.
7. Arithmetic: the threadpool has 40 threads; a `def` endpoint holds one for 3 s per call.
   At what sustained request rate does *every* endpoint in the process stall, and what are
   the two legitimate fixes?
8. What is BackgroundTasks' actual delivery contract — three properties? What mechanism do
   must-happen side effects ride instead, and where in Ledgerly's code was that mechanism
   already being written?
9. A new endpoint tests green, deploys clean, is never reached in production — yet appears in
   `/docs`. Explain both halves of that sentence.
10. Why is mapping the exception *type* `IntegrityError` to the business meaning "idempotency
    key reused" a time bomb? What must the mapping key on instead, and what happens to a
    violation the mapping doesn't recognise?
11. "Backpressure converts a pooled connection into a client-paced loan." Unpack the
    sentence, then give the per-route arithmetic rule that decides whether an endpoint may
    stream directly from the pool.
12. Lax coercion plus `float` money survived every unit test and failed at the tax office.
    Why did the tests pass, and which two Pydantic settings close the hole?
13. Invoice creation dropped 40% with zero server errors and empty logs. Why was a
    business-invariant baseline the *only* possible detector, and what CI test now prevents
    the root cause?
14. Write out Ledgerly's canonical middleware stack outermost-first, marking the layers the
    framework adds automatically.
15. Design the WebSocket close-code vocabulary: who sends 1011, 1001, and the 4400 range —
    and what makes 1006 fundamentally different from all of them?
16. *Mini coding challenge.* Sketch the IntegrityError handler: how a constraint violation
    becomes a `DomainError` carrying a 02.9 problem type, including the branch for an
    unrecognised constraint. Why is that branch a re-raise?
17. *Mini coding challenge.* Write the route-table test asserting every schema-visible route
    has a deliberate camelCase operation id. Why can't "the author passed `name=`" be tested
    directly?
18. *Design prompt.* Assemble `main.py` for a brand-new FastAPI service: settings, middleware
    order, exception handlers, routers, operation ids, docs/schema gating, lifespan. Justify
    each line's *position* by naming the module-03 incident that punished getting it wrong.

---

## Answers

1. The LAST middleware added is the OUTERMOST (03.7, verified by execution). Outermost put
   the audit middleware above `CORSMiddleware`, so it received preflights — which carry no
   `Authorization` — and its parse raised. Exceptions in middleware bypass the type-specific
   handlers (they live inside `ExceptionMiddleware`, further in), so every preflight was a
   bare 500 and the browser blocked the real requests.
2. (03.1) Import happens before the fork: workers share/corrupt connection state created by
   the parent; and import-time work makes the module unimportable without infrastructure —
   tests, scripts and tooling all pay, and any import-time network hiccup kills the process
   before it can even report.
3. Teardown after `yield` runs *after the response has left* (03.5). So nothing
   response-critical may live there — committing the transaction in teardown means the
   client's `201` races the commit, and a failed commit contradicts an already-sent success.
4. (03.12) An unhandled exception after `accept()` drops TCP with **no close frame**; the
   browser synthesises **1006** — nobody sends it — which is indistinguishable from a network
   blip, precisely what client reconnect logic retries instantly. A deterministic server bug
   thus acquires network-failure retry semantics: the storm.
5. One model per direction — `*In` and `*Out`, never one model doing create and update
   (03.3). `ResponseValidationError`: the handler returned something its `response_model`
   cannot validate, and FastAPI turns it into a 500 rather than shipping a malformed body.
6. "Fail fast on what you own; never gate startup on what can blip" (03.9). A bad config
   value is *yours* — failing early is correct. Redis's reachability is a dependency's
   uptime; pinging it in lifespan made a third party's maintenance window a precondition for
   any process starting, fleet-wide, exactly during a rolling deploy.
7. Saturation at 40 threads ÷ 3 s ≈ 13 req/s sustained (03.6): thread 41's request waits,
   and since *every* `def` endpoint shares the pool, all of them stall together. Fixes: make
   the endpoint `async` with a truly async client, or keep it `def` and size/isolate the
   pool deliberately.
8. At-most-once, in-process, unrecorded (03.10): a worker kill, deploy or crash deletes the
   task and leaves success-shaped silence. Must-happen effects ride the **outbox** row that
   03.5's service already writes in the business transaction; the relay (11.15) delivers
   with retries.
9. Route matching is first-wins over registration order: `/v1/invoices/{invoice_id}` was
   registered before `/v1/invoices/summary`, so the literal path never matches (03.2).
   OpenAPI is generated from the route *table*, not from reachability — the shadowed route
   is registered, therefore documented.
10. The equivalence "IntegrityError = key reused" is a property of the *schema* — true only
    while exactly one unique constraint exists on that path (03.8). Thursday's migration
    added a second, and its violations were reported (and acted on!) as idempotent replays.
    Map on the **constraint name**; unknown constraints re-raise to a 500, because a wrong
    answer is worse than no answer.
11. The client's read pace governs how fast the server may push; while it trickles, whatever
    the response generator holds — a pooled DB connection — stays held (03.11). One slow
    tenant's parallelism borrows the whole pool. Rule: `pool_size ÷ expected hold-time`
    must exceed the route's concurrency, written in the PR; if it can't, spool-then-stream.
12. Lax mode coerced the CSV's decimal strings into `float`, whose binary error only
    surfaces at sums and roundings the tests never exercised at tax-authority scale (03.4).
    `Decimal` for money and `strict=True` (plus constrained field types) close it.
13. The break lived in the *customers'* builds — their requests never arrived, so no server
    metric, log or error could fire; only a number with a same-weekday baseline notices
    absence (03.13). The CI test rejects any schema-visible route whose operation id looks
    like a snake_case function name — an id nobody chose.
14. RequestContextMiddleware → CORSMiddleware → CachePolicyMiddleware →
    TenantAuditMiddleware, with ServerErrorMiddleware (outermost of all),
    ExceptionMiddleware and AsyncExitStackMiddleware added automatically by the framework
    (03.7's constructor-list form; 03.1's assembly).
15. 1011 = our bug, sent explicitly by the handler catching itself; 1001 = going away, sent
    at shutdown/deploy so reconnect is guilt-free; 4400-range = documented deterministic
    verdicts on the client's payload — the close-code edition of the 02.9 catalogue. 1006 is
    **never sent by anyone**: it is the client's *name* for a frameless drop, which is why a
    server must never let one happen (03.12).
16. Catch `IntegrityError`, extract the constraint name from the driver diagnostics, look it
    up in a dict → `DomainError(problem_type=...)` from the 02.9 catalogue; on a miss,
    `raise` — an unmapped violation is an unknown schema fact, and labelling it with a
    familiar business meaning is exactly the 03.8 incident (03.8).
17. Parametrise over `[r for r in app.routes if isinstance(r, APIRoute) and
    r.include_in_schema]`; assert `route.name` matches `^[a-z]+(?:[A-Z][a-z0-9]+)+$` (or a
    grandfathered set). You can't test "explicit" directly because the default *is*
    `route.name` — a defaulted name and an explicit one are the same attribute; house style
    (snake vs camel) is the only mechanical tell (03.13).
18. Strong shape, in order: pure `get_settings()` (03.1); `FastAPI(lifespan=...)` creating
    resources post-fork, construct-only (03.9); `add_middleware` reading *backwards* so
    RequestContext lands outermost (03.7); `register_error_handlers` on Starlette's
    HTTPException + IntegrityError-by-constraint (03.8); routers with explicit `name=` on
    every route (03.2/03.13); `use_stable_operation_ids(app)` *after* all includes because it
    rewrites the assembled table (03.13); docs *and* schema gated on `expose_docs`
    (03.13's completed gate); nothing at import that opens a socket (03.1).
