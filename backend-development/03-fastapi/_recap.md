## Module recap

**Running system:** Ledgerly, continued from modules 01–02 — the invoicing API now actually built
in FastAPI: assembled in `main.py`, deployed on Swarm behind the 01.10 proxy, serving the module-02
contract to the dashboard, customer integrations and generated SDKs. Module 04 keeps the same
system and goes inside its event loop.

**What this module built up.** Module 02 specified the contract; module 03 made FastAPI express it
faithfully. The through-line is that **a framework is a stack of defaults, and every default is a
decision somebody else made**: how routes match, how input coerces, when teardown runs, where sync
work executes, which middleware sees a request first, what an exception type means, when resources
are created, what "background" promises, who ends a stream, what the schema advertises, and what
happens when a deploy says stop. Each notebook takes one of those decisions back.

**The incidents, and what each one taught.**

| # | Incident | The general lesson |
|---|---|---|
| 03.1 | An engine created at import is shared across forked workers; 2% of requests fail with varied DB errors | Resources are created per worker, in lifespan; `main.py` must be importable with no side effects |
| 03.2 | `/invoices/summary` ships tested and documented — and is never reached, shadowed by `/{invoice_id}` | Route matching is first-wins over registration order; the docs describe the table, not reachability |
| 03.3 | One model serves create and update; 1,847 invoices reconcile wrong with zero errors | One model per direction; `response_model` guards the contract both ways |
| 03.4 | Lax coercion admits CSV strings into `float` money; VAT filings rejected over one cent | Validation modes are contract decisions; money is `Decimal`, strict at the boundary |
| 03.5 | The commit lives in a dependency's teardown; a customer holds a `201` for an invoice that never existed | Code after `yield` runs after the response leaves — nothing response-critical belongs there |
| 03.6 | One `def` endpoint with a slow outbound call pins all 40 threads; pods cycle unhealthy at month-end | The threadpool is one shared budget; sync work is a loan the whole process co-signs |
| 03.7 | Audit middleware "added last so nothing escapes it" lands outermost — above CORS; every preflight 500s | Last added is outermost; exceptions in middleware bypass the typed handlers |
| 03.8 | `IntegrityError` means "idempotency key reused" — until a migration adds a second constraint | Map constraint *names*, not exception types; unknown violations re-raise |
| 03.9 | A `redis.ping()` in lifespan meets a provider failover mid-deploy; no process in the fleet can start | Fail fast on what you own; never gate startup on what can blip |
| 03.10 | Billing events ride BackgroundTasks; the August close finds invoices metering never saw | BackgroundTasks is at-most-once, in-process, unrecorded; must-happen work rides the outbox |
| 03.11 | 120 trickle-speed downloads hold the fleet's whole DB pool; the *successful* requests are the outage | Backpressure turns held resources into client-paced loans; do the pool ÷ hold-time arithmetic per route |
| 03.12 | A strict validator crashes accepted sockets; frameless drops read as 1006 → a 7,000/s reconnect storm | On a socket you are your own last handler; your bug in a network failure's clothes gets retried |
| 03.13 | A function-rename refactor renames operationIds; SDKs break; invoice creation drops 40% in silence | Generated defaults are public contract; only a business-invariant baseline notices absence |
| 03.14 | A shell-form `CMD` eats SIGTERM; 41 deploys, zero graceful shutdowns, and nothing ever said so | Every graceful path is dead code until the signal actually arrives — and only evidence proves it ran |

**The pattern across all fourteen.** In every incident the framework did *exactly what it was
told* — the failure was a default nobody had consciously accepted. Module 01's lesson was that
healthy-looking systems can be wrong; module 02's was that contract violations produce no
server-side signal; module 03 closes the loop: the way out is **enumerating the defaults and
deciding each one on purpose**, then pinning the decision with a test on the *assembled
application* — the route table, the middleware list, the built image — because unit tests of
handlers see none of these failures. The second recurring move is detection by **evidence of
absence**: the reconciliation that finds unsent invoices (03.10), the same-weekday baseline that
notices missing traffic (03.13), the 1001 counter reading zero (03.14). Silence is not success;
a graceful path that leaves no evidence of running must be treated as not running.

**Config invariants established here** (each asserted by a CI test in its notebook):

```text
main.py importable with no side effects; resources created in lifespan   (03.1, 03.9)
middleware as one constructor list; last-added = outermost               (03.7)
one Pydantic model per direction; response_model on every route          (03.3, 02.4)
money = Decimal; strict validation at public boundaries                  (03.4)
nothing response-critical after a dependency's yield                     (03.5)
every def endpoint justified against the shared 40-thread budget         (03.6)
IntegrityError mapped by constraint name; unknown → re-raise (500)       (03.8)
startup gates on owned config only, never dependency reachability        (03.9)
must-happen side effects ride the outbox, never BackgroundTasks          (03.10)
streaming routes pass pool ÷ hold-time, else spool-then-stream           (03.11)
every WS exit is an explicit close frame; Origin checked at handshake    (03.12)
explicit camelCase name= on schema-visible routes; openapi.json diffed   (03.13)
docs AND schema gated on expose_docs (docs_url + openapi_url)            (03.13)
exec-form CMD under tini; request < graceful < grace, asserted together  (03.14)
```

**Recurring cross-cutting threads picked up here.** *The outbox*: written by 03.5's service,
made mandatory by 03.10, drained by the relay in 11.15. *Deploys as scheduled failure events*:
03.9 (startup gates × stop-first), 03.12 (every socket severed), 03.14 (the signal path itself) —
module 14 owns the rollout machinery. *Telemetry that pays for itself*: 03.12's close-code
counters were built as incident prevention and became 03.14's only detector. *Assembled-app
tests*: 03.2's shadow check, 02.4/03.13's route-table and snapshot tests, 03.14's drain test —
a family that tests the object `main.py` builds, not the functions it imports.

**What module 04 assumes.** That you know requests share one event loop per worker with a
bounded threadpool escape hatch (03.6), that clients and engines live in lifespan-owned state
(03.9), that a blocked loop is a fleet incident rather than a slow endpoint, and that
cancellation is something your code must survive (03.12's TaskGroups, 03.14's drain deadline).
Module 04 goes inside that loop: finding the blocking call, request-scoped state, races between
concurrent requests, timeouts and cancellation done properly — and 04.9 picks up the drain
window 03.14 opened.
