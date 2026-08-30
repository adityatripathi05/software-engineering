"""Lab for 04.5 Race conditions in concurrent requests.

Reproduces the notebook's captures:
  A. the async atomicity rule: 100 concurrent increments with no await are
     exact; the same increment split across an await loses updates
  B. the token-refresh stampede against a single-active-token provider:
     naive check-then-refresh vs Lock+double-check vs shared-Task
     single-flight — issuances and failed calls counted
  C. asyncio.Queue as pacing: a bounded queue makes producers wait when the
     consumer falls behind (03.12's maxsize=256, measured)
  D. asyncio.Semaphore as a concurrency cap: 20 tasks, cap 5, max in-flight
     measured

Run:  python lab_04_05_races.py     (pure asyncio; no server)
"""
import asyncio
import time


# ---------- A. atomic between awaits -----------------------------------------
async def section_a() -> None:
    print("A. 100 concurrent increments of a shared counter")
    counter = {"n": 0}

    async def bump_no_await() -> None:
        counter["n"] += 1                     # read-modify-write, no await inside

    async def bump_across_await() -> None:
        n = counter["n"]                      # read
        await asyncio.sleep(0)                # ⚠️ the hazard window
        counter["n"] = n + 1                  # write back a stale value

    async with asyncio.TaskGroup() as tg:
        for _ in range(100):
            tg.create_task(bump_no_await())
    no_await = counter["n"]

    counter["n"] = 0
    async with asyncio.TaskGroup() as tg:
        for _ in range(100):
            tg.create_task(bump_across_await())
    print(f"   no await inside the operation : {no_await}/100")
    print(f"   one await inside the operation: {counter['n']}/100")
    print("  => between awaits, async code is ATOMIC (04.1: no preemption);")
    print("     the race lives exactly at the await point (04.5)\n")


# ---------- B. the refresh stampede ------------------------------------------
class TaxProvider:
    """Single-active-token policy: issuing a new token invalidates the old one
    (and issuance takes real time, like any OAuth token endpoint)."""

    def __init__(self) -> None:
        self.issued = 0
        self.active: str | None = None

    async def issue_token(self) -> str:
        await asyncio.sleep(0.05)             # the token endpoint round-trip
        self.issued += 1
        self.active = f"tok_{self.issued:03d}"
        return self.active

    def accepts(self, token: str) -> bool:
        return token == self.active


async def run_stampede(strategy: str, provider: TaxProvider) -> tuple[int, int]:
    cache: dict = {"token": None, "task": None}
    lock = asyncio.Lock()
    failures = 0

    async def get_token() -> str:
        if strategy == "naive":
            if cache["token"] is None or not provider.accepts(cache["token"]):
                cache["token"] = await provider.issue_token()     # herd refreshes
            return cache["token"]
        if strategy == "lock":
            if cache["token"] and provider.accepts(cache["token"]):
                return cache["token"]
            async with lock:
                if cache["token"] and provider.accepts(cache["token"]):
                    return cache["token"]                          # double-check
                cache["token"] = await provider.issue_token()
                return cache["token"]
        # single-flight: everyone awaits the SAME refresh task
        if cache["token"] and provider.accepts(cache["token"]):
            return cache["token"]
        if cache["task"] is None or cache["task"].done():
            cache["task"] = asyncio.create_task(provider.issue_token())
        cache["token"] = await cache["task"]
        return cache["token"]

    async def tax_call() -> None:
        nonlocal failures
        token = await get_token()
        await asyncio.sleep(0.01)             # the actual rate lookup, using token
        if not provider.accepts(token):
            failures += 1                     # 401: someone re-issued meanwhile

    async with asyncio.TaskGroup() as tg:
        for _ in range(30):                   # the hourly expiry boundary
            tg.create_task(tax_call())
    return provider.issued, failures


async def section_b() -> None:
    print("B. 30 concurrent tax calls hitting an expired token")
    for strategy in ("naive", "lock", "single-flight"):
        issued, failures = await run_stampede(strategy, TaxProvider())
        print(f"   {strategy:13} -> token issuances: {issued:2d}   "
              f"calls failing 401: {failures:2d}/30")
    print("  => naive check-then-act across the refresh await: a 30-wide herd,")
    print("     each new token invalidating the last — mutual 401s. One lock")
    print("     with a double-check (or one shared task) makes it one refresh (04.5)\n")


# ---------- C. bounded queue = backpressure ----------------------------------
async def section_c() -> None:
    print("C. bounded asyncio.Queue: producers pace to the consumer")
    queue: asyncio.Queue[int] = asyncio.Queue(maxsize=4)          # 03.12's shape
    put_waits: list[float] = []

    async def producer() -> None:
        for i in range(12):
            t0 = time.monotonic()
            await queue.put(i)
            put_waits.append((time.monotonic() - t0) * 1000)

    async def consumer() -> None:
        for _ in range(12):
            await queue.get()
            await asyncio.sleep(0.02)                             # slow writer task

    async with asyncio.TaskGroup() as tg:
        tg.create_task(producer())
        tg.create_task(consumer())
    fast = sum(1 for w in put_waits if w < 1)
    print(f"   12 puts into maxsize=4: {fast} returned instantly, "
          f"{12 - fast} BLOCKED (waits up to {max(put_waits):.0f} ms)")
    print("  => a full bounded queue makes the producer wait: backpressure by")
    print("     construction — the unbounded version hides the same imbalance")
    print("     as memory growth (03.12, 04.5)\n")


# ---------- D. semaphore = concurrency cap -----------------------------------
async def section_d() -> None:
    print("D. asyncio.Semaphore(5) over 20 concurrent calls")
    sem = asyncio.Semaphore(5)
    in_flight = {"now": 0, "max": 0}

    async def call() -> None:
        async with sem:
            in_flight["now"] += 1
            in_flight["max"] = max(in_flight["max"], in_flight["now"])
            await asyncio.sleep(0.02)
            in_flight["now"] -= 1

    async with asyncio.TaskGroup() as tg:
        for _ in range(20):
            tg.create_task(call())
    print(f"   observed max in-flight: {in_flight['max']} (cap 5)")
    print("  => the 04.3 mitigation, named: a semaphore is a pool with no")
    print("     objects — pure concurrency budget (04.5)")


if __name__ == "__main__":
    asyncio.run(section_a())
    asyncio.run(section_b())
    asyncio.run(section_c())
    asyncio.run(section_d())
