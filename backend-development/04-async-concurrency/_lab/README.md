# Module 04 lab

Runnable scripts that reproduce the notebooks' captured transcripts (AUTHORING-GUIDE §4.4).
Run each with plain `python <script>.py`; server-based sections start and stop their own
uvicorn.

| Script | Notebook | Reproduces |
|---|---|---|
| `lab_04_01_event_loop.py` | 04.1 | Task interleaving on one thread · the lag law measured (lag ≈ tasks × slice) · debug mode naming a 50 ms slice · a bystander `/ping` taxed by big-page serialisation, restored by the page cap (uvicorn, port 8175) |
| `lab_04_02_blocking.py` | 04.2 | The three tiers measured against a real 2 s provider: shared-client await (4 ms bystander) vs per-request `AsyncClient` (~380 ms hidden sync SSL build) vs sync-in-async (full freeze) · `faulthandler.dump_traceback_later` naming the frozen frame (`httpcore/_backends/sync.py … read`) · the sampler's gap-then-giant-sample view of a freeze · the import guard (uvicorn 8177, provider 8176) |
| `lab_04_03_pools.py` | 04.3 | httpx pool exhaustion measured (5 borrow for 2 s, 3 fail fast at `PoolTimeout`) · the head-of-line proof: a 50 ms dependency dying at 1 s behind a degraded one on a shared client vs 71 ms bulkheaded · the real client defaults (`max_connections=100`, `Timeout(5.0)` incl. the silent pool phase) · SQLAlchemy's canonical `QueuePool limit … reached` timeout (provider on 8178) |
| `lab_04_04_contextvars.py` | 04.4 | The bleed measured: `threading.local` wrong 39/40 after one await, `ContextVar` 0/40 · snapshot inheritance (child keeps `t_44f1` after parent moves on) · the propagation matrix (raw executor loses context, anyio/`def`-endpoint path carries it) · six interleaved server requests with the ctxvar column right and the thread-local column last-writer-wins, plus the stale-leak probe (uvicorn 8179) |
| `lab_04_05_races.py` | 04.5 | The atomicity rule measured: 100/100 increments with no await, 1/100 across one await · the refresh stampede vs a single-active-token provider (naive: 30 issuances, 29/30 calls 401; lock and single-flight: 1 issuance, 0 failures) · bounded-queue backpressure (7 of 12 puts block) · `Semaphore(5)` capping observed in-flight at exactly 5 |
| `lab_04_06_lost_updates.py` | 04.6 | Two real connections, deterministic interleave: the lost update (the 40 is gone; atomic expression restores 100) · the send-vs-void race (naive: void overwritten AND email sent; CAS: rowcount elects one winner, loser ships nothing) · the unique constraint arbitrating a double reminder (named IntegrityError) · the version column (both read v1; rowcounts 1 and 0) |
| `lab_04_07_cpu_bound.py` | 04.7 | The four-home matrix under the lag sampler: inline (max lag = task length), thread+GIL-holding (~21 ms limp on every slice), thread+GIL-releasing kdf and process pool (both at the floor) · `sys.getswitchinterval()` · process-pool economics: ~550 ms cold spawn, 1.5 ms warm round-trip, overhead vanishing into a real 250 ms task |
