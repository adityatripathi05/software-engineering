## Module recap

**Running system:** Ledgerly, continued — the invoicing API from modules 01–03, now examined
from inside its event loop: the same replicas, dependencies (tax provider, PDF renderer) and
deploys, instrumented down to the slice. Module 05 keeps the system and descends into PostgreSQL.

**What this module built up.** Module 03 taught that the framework's defaults are decisions;
module 04 taught that **concurrency's hazards have addresses**. Between awaits, async code is
atomic; *at* every await, the world may change — and that one fact generates the whole module:
races live at awaits (04.5), context must travel across them (04.4), cancellation lands on them
(04.8), the loop queues behind the code between them (04.1), and everything that never awaits —
sync calls (04.2), CPU burns (04.7) — holds the only thread hostage. The module's method was as
important as its content: **every claim was measured**, and twice the measurements corrected the
module's own earlier code — 04.8's lab proved that cancelling a waiter kills the shared task it
awaits, amending 04.5's TokenCache with a shield. Measure, don't assert, applied to ourselves.

**The incidents, and what each one taught.**

| # | Incident | The general lesson |
|---|---|---|
| 04.1 | Quarter-end report pages triple p99 on *every* route at once; host CPU reads 13% | Loop lag ≈ queue depth × slice length, paid by all; uniform degradation means the shared queue — graph the loop, cap the page |
| 04.2 | A sync vendor SDK freezes replicas in waves when the provider slows; probes flake, restarts churn | `async def` promises nothing about callees; the stack dump ends the argument; mocks at the service seam certify the bug |
| 04.3 | The renderer's bad morning fails "tax timeouts" while the tax provider is healthy | `PoolTimeout` means *us*: one shared client is shared fate — a client per dependency is a bulkhead; span == configured timeout ⇒ pure queue |
| 04.4 | A SOC2 reviewer finds other tenants' actions in their audit export — 7% of rows mislabelled | A thread-local under one thread is last-writer-wins (39/40 wrong, measured); ContextVar copies per task; behaviour via parameters, telemetry via context |
| 04.5 | Tax fails 90 s at :47 past every hour — deploy-aligned token TTLs herd 350 refreshes into a 10/min endpoint | Every check-then-act across an await is a stampede at concurrency N; single-flight or lock+double-check; jitter every self-set TTL |
| 04.6 | A voided €14,300 invoice is emailed anyway; the void is silently overwritten | Reads are photographs: CAS with rowcount as the verdict, constraints as arbiters, side effects riding the winning transaction |
| 04.7 | A KDF lands on API-key auth inline; the lag alert pages in 4 minutes; 9-minute incident | CPU has four homes with measured signatures; GIL release is a per-library fact; KDF cost defends guessable secrets only |
| 04.8 | Renderer brownout: 3 tries × 10 s outlive the 30 s edge; the fleet computes 2.7 responses per one delivered | Deadlines must nest (edge > handler > Σ tries×per-try); retries spend budgets; zombies hold pools for nobody |
| 04.9 | Eleven deploys each silently delete 30–60 queued audit rows; a completeness check finds the clusters | Drain order is the data-loss policy (stop intake → flush → cancel, measured 15 vs 0 lost); must-happen records never ride in-process queues |
| 04.10 | An async rewrite duplicates finance's summaries at *identical* runtime | Concurrency is a property of workload and resources, not syntax; `gather` over one session buys errors at zero speed; unchanged runtime = unmoved bottleneck |

**The pattern across all ten.** The failures sorted into a **signature taxonomy** the on-call can
read in one glance: uniform slowdown + smooth lag + pegged core = slices (04.1); wave-stalls +
sampler gaps + idle CPU = a blocking call (04.2); concentrated slowdown + flat lag = a slow
dependency, and span-duration == configured-timeout = your own pool's queue (04.3); load-shaped
wrong data with zero errors = interleaving (04.4/04.6); strictly periodic self-healing failure =
a synchronised cache (04.5). And the instruments built in the first two notebooks — the lag
sampler, the gap alert, the stack-dump runbook, the strict-loop CI fixture — compounded: the
04.7 incident lasted **nine minutes** because 04.1's alert and 04.2's runbook already existed.
Observability is the module's compound interest.

**Config and code invariants established here** (each asserted by a CI test in its notebook):

```text
slice budget: no await-free stretch > 20ms; whole suite under a strict loop  (04.1)
loop-lag sampler always-on + alert; metric ABSENCE alerts too                (04.1, 04.2)
no sync-I/O imports in request-path modules (requests, urllib3, psycopg2…)   (04.2)
threading.local banned in request paths; identity bleeds tested by interleave (04.4)
one client per dependency; explicit Limits + complete four-phase Timeout      (04.3)
single-flight caches: double-check, failure-clearing, SHIELDED awaits         (04.5, 04.8)
jitter every TTL the process sets for itself                                  (04.5)
guarded writes read rowcount; a constraint under every at-most-once           (04.6)
state transitions via CAS; side effects inside the winning transaction        (04.6)
CPU: GIL-release measured per library; process pool lifespan-owned & warmed   (04.7)
deadlines nest — edge > handler (must EXIST) > Σ(per-try × tries), in CI      (04.8)
retries spend from budgets (with_retries); zombie ratio ≈ 1.0 alerted         (04.8)
drain phases: stop intake → flush (capped, logged) → cancel (refusers NAMED)  (04.9)
teardown in reverse-startup order; shutdown has a mid-traffic harness test    (04.9)
must-happen records ride the transaction/outbox, never in-process queues      (04.9)
every gather/TaskGroup names its resource budget in the PR                    (04.10)
```

**Recurring cross-cutting threads picked up here.** *The reliability ladder becomes code*:
`with_retries` (04.8) finally implements "retries without a budget make outages worse", promised
since module 01. *The absence-detector family grows*: the zombie ratio (04.8), the audit
completeness invariant (04.9), `token_refreshes_total` (04.5) — all descendants of 03.13's
lesson that silence needs its own metrics. *The boundary ladder*: 04.5's primitives coordinate
one process, 04.6's database coordinates replicas, 10.12's Redis locks wait beyond — each
notebook naming where its tools stop. *Canon self-correction as method*: 04.8 amended 04.5's
shipped code by measurement, as 02.5 and 03.12 were amended before.

**What module 05 assumes.** That a session/connection is single-flight property (04.10), that
CAS + rowcount + constraints are your reflexes for concurrent writes (04.6), that pool
arithmetic is second nature (04.3), and that you can tell a slow query from a starved pool from
a frozen loop by telemetry alone. Module 05 brings the real engine: PostgreSQL under the
module's first `compose.yaml` (AUTHORING-GUIDE §4.4), where isolation levels, `FOR UPDATE`, and
the query planner give the 04.6 story its full depth.
