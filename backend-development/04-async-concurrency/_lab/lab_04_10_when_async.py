"""Lab for 04.10 When async helps and when it does not.

Reproduces the notebook's captures:
  A. the payoff: 200 concurrent requests against a 100ms I/O dependency —
     async rides them all at once; def endpoints queue behind 40 threads
  B. the non-payoff: the same comparison with 30ms of CPU per request —
     nobody wins; async cannot buy throughput for burning (04.7)
  C. what waiting costs: 10,000 concurrent sleeping tasks, timed
  D. the incident's mechanism: gather() over ONE shared connection —
     errors, retries, and zero speedup (the connection serialises anyway)

Run:  python lab_04_10_when_async.py     (uvicorn on 8181 for A/B)
"""
import asyncio
import statistics
import subprocess
import sys
import time
from pathlib import Path

from fastapi import FastAPI

app = FastAPI()
CPU_N = 140_000                       # ~30ms of bytecode on this machine
INFLIGHT: dict[str, dict] = {}


class Gauge:
    """max-in-flight per endpoint: the server's own view of concurrency,
    immune to client-side request overhead."""

    def __init__(self, name: str) -> None:
        self.d = INFLIGHT.setdefault(name, {"now": 0, "max": 0})

    def __enter__(self):
        self.d["now"] += 1
        self.d["max"] = max(self.d["max"], self.d["now"])

    def __exit__(self, *a):
        self.d["now"] -= 1


@app.get("/stats")
async def stats() -> dict:
    return {k: v["max"] for k, v in INFLIGHT.items()}


@app.get("/io-async")
async def io_async() -> dict:
    with Gauge("io-async"):
        await asyncio.sleep(0.1)      # the awaited dependency
    return {"ok": True}


@app.get("/io-def")
def io_def() -> dict:
    with Gauge("io-def"):
        time.sleep(0.1)               # same dependency, threadpool seat (03.6)
    return {"ok": True}


@app.get("/cpu-async")
async def cpu_async() -> dict:
    sum(i * i for i in range(CPU_N))
    return {"ok": True}


@app.get("/cpu-def")
def cpu_def() -> dict:
    sum(i * i for i in range(CPU_N))
    return {"ok": True}


# ---------- A + B: the head-to-head ------------------------------------------
async def hammer(path: str, n: int = 200) -> tuple[float, float, float]:
    import httpx

    limits = httpx.Limits(max_connections=n, max_keepalive_connections=n)
    async with httpx.AsyncClient(limits=limits, timeout=60) as client:

        async def one(record: list[float] | None) -> None:
            t = time.monotonic()
            await client.get(f"http://127.0.0.1:8181{path}")
            if record is not None:
                record.append((time.monotonic() - t) * 1000)

        async with asyncio.TaskGroup() as tg:           # warm n keepalive conns
            for _ in range(n):                          # (fresh TCP connects would
                tg.create_task(one(None))               #  dominate the measurement)
        latencies: list[float] = []
        t0 = time.monotonic()
        async with asyncio.TaskGroup() as tg:
            for _ in range(n):
                tg.create_task(one(latencies))
        wall = time.monotonic() - t0
    latencies.sort()
    return wall, statistics.median(latencies), latencies[int(n * 0.95)]


def sections_a_b() -> None:
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "lab_04_10_when_async:app",
         "--port", "8181", "--log-level", "warning"],
        cwd=Path(__file__).parent, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        import httpx
        for _ in range(40):
            try:
                httpx.get("http://127.0.0.1:8181/io-async", timeout=2)
                break
            except Exception:
                time.sleep(0.5)

        print("A. 200 concurrent requests, dependency waits 100ms (the I/O shape)")
        print(f"   {'endpoint':10} {'wall':>7}   max in-flight (server's view)")
        for path in ("/io-async", "/io-def"):
            wall, _, _ = asyncio.run(hammer(path))
            mx = httpx.get("http://127.0.0.1:8181/stats", timeout=5).json()
            print(f"   {path:10} {wall:6.2f}s   {mx[path.strip('/')]:3d} concurrent waits held")
        print("  => the server tells the truth the client's overhead hides: async")
        print("     parks ~200 waits at once; def is hard-capped at its 40 thread")
        print("     seats (03.6) — 5 waves through the dependency\n")

        print("B. same 200 requests, 30ms of CPU each (the burning shape)")
        print(f"   {'endpoint':10} {'wall':>7} {'p50':>8} {'p95':>8}")
        for path in ("/cpu-async", "/cpu-def"):
            wall, p50, p95 = asyncio.run(hammer(path))
            print(f"   {path:10} {wall:6.2f}s {p50:7.0f}ms {p95:7.0f}ms")
        print("  => one core, 6s of total burning: async serialises it on the loop,")
        print("     def limps it through the GIL (04.7) — NOBODY wins; async cannot")
        print("     buy throughput for work that never waits\n")
    finally:
        proc.kill()


# ---------- C: what waiting costs --------------------------------------------
async def section_c() -> None:
    print("C. the price of holding 10,000 concurrent waits")
    t0 = time.monotonic()
    async with asyncio.TaskGroup() as tg:
        for _ in range(10_000):
            tg.create_task(asyncio.sleep(0.2))
    print(f"   10,000 sleeping tasks created, held and completed in "
          f"{time.monotonic()-t0:.2f}s total")
    print("  => a parked task is a heap object, not a thread: waiting in bulk is")
    print("     nearly free — this is the entire economic case for async (04.10)\n")


# ---------- D: gather over one connection ------------------------------------
class OneConnection:
    """asyncpg's law, miniaturised: one operation at a time per connection."""

    def __init__(self) -> None:
        self.busy = False

    async def execute(self, q: str) -> None:
        if self.busy:
            raise RuntimeError("another operation is in progress")
        self.busy = True
        try:
            await asyncio.sleep(0.02)          # the query holds the connection
        finally:
            self.busy = False


async def section_d() -> None:
    print("D. the rewrite's mechanism: gather() over ONE shared connection")
    conn = OneConnection()

    # gather + retry-until-done: what the rewrite's error handling amounted to
    t0 = time.monotonic()
    pending, attempts, errors = list(range(20)), 0, 0
    while pending:
        results = await asyncio.gather(
            *(conn.execute(f"INSERT summary {i}") for i in pending),
            return_exceptions=True)
        attempts += len(pending)
        failed = [i for i, r in zip(pending, results) if isinstance(r, Exception)]
        errors += len(failed)
        pending = failed
    gather_wall = time.monotonic() - t0

    t0 = time.monotonic()
    for i in range(20):
        await conn.execute(f"INSERT summary {i}")
    seq_wall = time.monotonic() - t0

    print(f"   gather + retries over 1 connection: {gather_wall:.2f}s, "
          f"{attempts} attempts, {errors} 'operation in progress' errors")
    print(f"   plain sequential loop             : {seq_wall:.2f}s, 20 attempts, 0 errors")
    print("  => the connection serialises the work regardless: gather added the")
    print("     errors (and the retry-shaped duplicates) and ZERO speed. The")
    print("     workload's concurrency was 1 all along (04.10)")


if __name__ == "__main__":
    sections_a_b()
    asyncio.run(section_c())
    asyncio.run(section_d())
