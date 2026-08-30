# Module 04 — Self-Test

Retrieval practice for [Async & Concurrency](README.md). Attempt every question — aloud or on
paper — **before** opening the Answers at the bottom. This module's claims were all measured;
several questions ask you to reproduce the *numbers'* logic, not just the words. If you can
re-derive a lab result's shape, you own the mechanism.

**How to use these notes:** state your own Mental Model before reading the given one · answer
Interview Questions aloud before the answer shape · run at least one `_lab/` script per
notebook (they exist for exactly this) · reattempt this quiz a week later.

---

## Questions

1. Failing tax spans last exactly 5.000 s, contain no connection events, and the tax provider
   is demonstrably healthy. Which timeout fired, what does it tell you, and whose pager should
   ring?
2. Derive the loop-lag law from the loop's iteration, then give the three telemetry signatures
   that distinguish: a slow awaited dependency · slice pressure · an exhausted threadpool.
3. Why is ORM get-mutate-flush a race in respectable clothing? What replaces it, and what must
   every caller of the replacement read?
4. The sync vendor SDK shipped through a fully green test suite. Explain precisely how — and
   name the guard that catches this class *without executing anything*.
5. Tax calls fail for ninety seconds at :47 past every hour, worse under load, self-healing.
   Walk the trigger arithmetic and give both the config-only mitigation and the permanent fix.
6. State the deadline-nesting inequality, say which term uvicorn does NOT provide, and explain
   what a zombie ratio of 2.7 measures.
7. In the 04.4 lab, 39 of 40 concurrent tasks woke up believing they were someone else. State
   the mechanism to the line, and the ContextVar property that makes the same code return 0/40.
8. Lay out 04.7's four-home matrix with the measured lag signature of each row. Which row ships
   silently through light testing, and why?
9. Order the drain phases of a correct in-process shutdown and attach to each boundary the loss
   mode that reordering it causes.
10. The two questions that decide whether async fits a workload — and what does an *unchanged*
    runtime after a "performance rewrite" prove?
11. What does cancelling a task do to the future it is currently awaiting? State the measured
    consequence for a shared single-flight task, and the one-call fix.
12. Distinguish 04.1's incident telemetry from 04.2's: lag shape, CPU, probes, and what the
    sampler shows during each.
13. Why must the outbox enqueue live inside the same transaction as the CAS status transition?
    What becomes unrepresentable when it does?
14. Give the loan-desk reading of a connection pool: the four numbers that define one, the
    sizing arithmetic, and what "span duration equals configured timeout" always means.
15. When is a *fast* hash the secure choice — and what, exactly, does KDF slowness purchase?
16. Which loss can an ordered drain not prevent, and which contract decision closes it?
17. Draw the context propagation matrix: where a ContextVar's value follows the work for free,
    where it silently doesn't, and the remedy at each non-crossing boundary.
18. *Mini coding challenge.* Sketch the final TokenCache (post-04.8): fast path, single-flight
    gate, failure clearing, shield — one sentence per line on the incident each prevents.
19. *Mini coding challenge.* Sketch `with_retries`' budget arithmetic and state the property it
    enforces that no amount of future `tries=` tuning can break.
20. p99 has tripled uniformly across every route; host CPU reads 13%; no errors. Name the first
    metric you read, the number on it that confirms the diagnosis, and the two dashboards it
    lets you skip.
21. *Design prompt.* Assemble the async-hazard tooling kit you would ship with any new async
    service — at least six items — mapping each to the module-04 incident it prevents or
    shortens.

---

## Answers

1. `httpx.PoolTimeout` at the 5 s default: the request queued at your own client's pool and
   never reached the network — the culprit is whoever holds the loans (another dependency's
   slow calls), and the pager is yours, not the tax provider's (04.3).
2. Each iteration drains the ready queue one slice at a time, so lag ≈ depth × slice, added to
   every request at every await. Dependency: slowdown concentrated in its callers, lag flat.
   Slices: uniform absolute slowdown, smooth elevated lag, one core pegged. Threadpool: `def`
   routes stall together, async routes fine (04.1, 03.6).
3. The flush emits an *unguarded* UPDATE computed from a stale read — check in Python, act in
   SQL. Replace with `update().where(expected_state)` (or the version column) and every caller
   must read **rowcount**: 0 is the race telling you that you lost (04.6).
4. The SDK entered through a seam the tests faked (service-level mock), so its `requests`
   sockets never executed under the strict-loop fixture. The import guard — blocklisted sync-I/O
   imports in request-path modules — needs no execution and fails in seconds (04.2).
5. Monday's 16:47 deploy synchronised every replica's token TTL; each hourly expiry made ~30
   concurrent calls per replica all pass the stale check and refresh — ~350 calls into a 10/min
   endpoint. Mitigation: refresh margin + per-replica jitter (desynchronise). Permanent:
   single-flight refresh — one task, N waiters (04.5).
6. `slowest request < Σ(per-try × tries) + slack < handler budget < edge timeout` — and the
   handler budget is the term uvicorn does not provide; you add it (DeadlineMiddleware). Zombie
   ratio = app-completed ÷ edge-delivered responses: 2.7 means the fleet computes almost three
   results per one anyone receives — capacity serving nobody (04.8).
7. One thread runs all tasks (04.1); `threading.local` is storage on that thread, so between a
   task's write and its read-after-await, every interleaved task's write lands on the same slot
   — last writer wins. A ContextVar reads from the current task's *copied* Context: writes stay
   in the copy, so interleaving cannot cross tasks (04.4).
8. Inline: frozen — max lag = task duration. Thread + GIL-holding: the limp — ~20 ms median lag
   (5 ms switch interval contention). Thread + GIL-releasing: floor. Process pool: floor plus
   freight. Row two ships silently: no freeze, no alert at light load, a fleet-wide latency
   floor in production (04.7).
9. Stop intake first (or flushed queues refill); flush owned queues under caps (or accepted work
   dies with its writer — measured 15 lost); cancel with grace and *name refusers* (or the hang
   is a mystery SIGKILL); close resources in reverse-startup order (or dying cleanups find
   closed clients); budget the unhurriable executor wait (or the guillotine lands mid-teardown)
   (04.9).
10. Does it wait, and do the waits overlap? Unchanged runtime proves the bottleneck was never
    what the rewrite changed — the work is resource- or sequence-bound, and the rewrite
    delivered risk at zero yield (04.10).
11. It cancels that future too — measured: a cancelled waiter killed the shared refresh
    (`flight.cancelled()=True, issued=[]`). Fix: waiters `await asyncio.shield(flight)` — the
    waiter dies free while the flight lives for everyone else (04.8, amending 04.5).
12. 04.1: smooth elevated lag, no gaps, core pegged, probes fine — queueing. 04.2: wave-stalls,
    sampler *gaps* with one giant edge sample, CPU idle, probes flaking into restarts — a
    frozen loop. The sampler cannot report during a freeze; its silence is the signal (04.2).
13. So the side effect exists iff the transition committed: rowcount-0 losers never enqueue,
    winners enqueue exactly once — "half an action" (email without status, status without
    email) becomes unrepresentable (04.6, 03.10).
14. Limits (loans that exist), hold-time (how long each is out), queue, and pool timeout (how
    long to stand in line). Size by `limits ÷ hold-time ≥ peak demand`, bounded by courtesy to
    the dependency. Span == configured timeout: the whole span was queue — it never touched the
    network (04.3).
15. When the secret is high-entropy (random API keys/tokens): KDF slowness prices *guessing*,
    and a 2^256 space cannot be guessed — slow hashing there is pure self-inflicted latency.
    Entropy decides the hash's speed, not pattern-matching (04.7).
16. Crash loss (SIGKILL, OOM): the drain never runs, and whatever an in-process queue holds is
    destroyed. Closed only by the carrier decision — must-happen records ride the request
    transaction or the outbox (04.9, 03.10).
17. Free: child tasks (snapshot at creation), TaskGroup children, `BackgroundTasks`, anyio
    threads / `def` endpoints. Not crossing: raw `run_in_executor` (wrap in
    `copy_context().run`), processes and queues (identity travels in the payload,
    explicitly) — and request-spawned long-lived tasks *shouldn't* inherit at all: start them
    from lifespan (04.4).
18. Fast path returns a valid token with no coordination (races cost nothing when healthy);
    `done()`-checked `create_task` = one flight however many arrive (the :47 herd);
    `await asyncio.shield(self._refresh)` = an impatient waiter cannot kill the herd's flight
    (04.8's measurement); `except: self._refresh = None; raise` = one failed refresh doesn't
    poison every future caller (04.5).
19. Compute a deadline once; each attempt's timeout is `min(per_try, remaining)`; an attempt
    that cannot fit the remainder is not started. Property: total spend ≤ budget by
    construction — `tries` can be tuned to anything and the sum still cannot exceed what the
    caller granted (04.8).
20. `event_loop_lag_ms`: p50 elevated (40–60 ms) and smooth confirms loop queueing, letting you
    skip every dependency dashboard (uniform degradation already exonerated them) and the host
    CPU graph (one pegged core hides in an eight-core average) (04.1).
21. Strong shape: lag sampler + alert + *gap* alert (04.1/04.2's minutes-not-hours payoff);
    strict-loop CI fixture with real hot-path dependencies (04.1/04.7's faked-auth gap); sync-
    I/O and `threading.local` import guards (04.2/04.4); per-dependency client registry test —
    bounded limits, four-phase timeouts (04.3); budget-nesting CI test + `with_retries` (04.8);
    mid-traffic SIGTERM drain harness + completeness invariants per must-happen stream (04.9);
    shared-session/single-flight detectors (04.10/04.5). Each maps to the incident that taught
    it; together they are why 04.7 cost nine minutes.
