"""Lab for 04.7 CPU-bound work and event-loop blocking.

Reproduces the notebook's captures:
  A. the strategy matrix: the same CPU work run four ways, with the 04.1
     lag sampler watching the loop — inline (frozen), thread + GIL-holding
     work (limping), thread + GIL-releasing work (clean), process (clean)
  B. the GIL's switch interval: why a GIL-holding thread degrades rather
     than freezes the loop
  C. process-pool economics: creation vs warm submit vs the work itself
     (why the pool is built in lifespan, never per request)

Run:  python lab_04_07_cpu_bound.py
"""
import asyncio
import concurrent.futures
import hashlib
import statistics
import sys
import time


# ---------- two calibrated CPU tasks -----------------------------------------
def pure_python_work() -> int:
    """~300ms of bytecode: holds the GIL for its entire duration."""
    return sum(i * i for i in range(1_200_000))


def kdf_work() -> bytes:
    """~300ms inside OpenSSL: hashlib.pbkdf2_hmac RELEASES the GIL."""
    return hashlib.pbkdf2_hmac("sha256", b"key_live_7ac", b"salt", 260_000)


# ---------- the sampler (04.1's, inlined) ------------------------------------
async def lag_while(coro_factory) -> tuple[float, float, float]:
    """Run the strategy; return (task_wall_s, median_lag_ms, max_lag_ms)."""
    lags: list[float] = []
    done = asyncio.Event()

    async def sampler() -> None:
        while not done.is_set():
            t0 = time.monotonic()
            await asyncio.sleep(0.01)
            lags.append((time.monotonic() - t0 - 0.01) * 1000)

    s = asyncio.create_task(sampler())
    await asyncio.sleep(0.05)                # let the sampler establish its rhythm
    t0 = time.monotonic()
    await coro_factory()
    wall = time.monotonic() - t0
    await asyncio.sleep(0.02)                # let a post-task sample land
    done.set()
    await s
    return wall, statistics.median(lags or [0]), max(lags or [0])


async def section_a(pool: concurrent.futures.ProcessPoolExecutor) -> None:
    loop = asyncio.get_running_loop()

    async def inline() -> None:
        pure_python_work()                              # on the loop thread

    async def thread_holding() -> None:
        await loop.run_in_executor(None, pure_python_work)

    async def thread_releasing() -> None:
        await loop.run_in_executor(None, kdf_work)

    async def process_pool() -> None:
        await loop.run_in_executor(pool, pure_python_work)

    print("A. one ~250ms CPU task, four homes — the loop's lag while it runs")
    print(f"   {'strategy':34} {'wall':>6}  {'lag p50':>8}  {'lag max':>8}")
    for name, strat in [
        ("inline in the handler", inline),
        ("thread + GIL-HOLDING work", thread_holding),
        ("thread + GIL-RELEASING work (kdf)", thread_releasing),
        ("process pool (pure python)", process_pool),
    ]:
        wall, p50, mx = await lag_while(strat)
        print(f"   {name:34} {wall:5.2f}s  {p50:6.1f}ms  {mx:6.1f}ms")
    print("  => inline freezes the loop for the whole task; a GIL-holding thread")
    print("     makes the loop LIMP (they share the interpreter); GIL-releasing")
    print("     native work and process pools leave it clean (04.7)\n")


def section_b() -> None:
    print("B. why the GIL-holding thread limps instead of freezing")
    print(f"   sys.getswitchinterval() = {sys.getswitchinterval()*1000:.0f} ms")
    print("  => the interpreter offers a GIL handover every 5ms of bytecode; the")
    print("     loop runs in the gaps — alive, but taxed on every slice (04.7)\n")


def section_c(pool: concurrent.futures.ProcessPoolExecutor) -> None:
    print("C. process-pool economics (Windows spawn)")
    t0 = time.perf_counter()
    fresh = concurrent.futures.ProcessPoolExecutor(max_workers=2)
    fresh.submit(int, 1).result()                       # forces worker start-up
    cold = (time.perf_counter() - t0) * 1000
    t0 = time.perf_counter()
    fresh.submit(int, 1).result()
    warm = (time.perf_counter() - t0) * 1000
    fresh.shutdown()
    t0 = time.perf_counter()
    pool.submit(pure_python_work).result()
    work = (time.perf_counter() - t0) * 1000
    print(f"   create pool + first trivial submit : {cold:7.1f} ms")
    print(f"   warm trivial submit round-trip     : {warm:7.1f} ms")
    print(f"   warm submit of the real 250ms task : {work:7.1f} ms")
    print("  => worker start-up costs hundreds of ms and pickling costs every")
    print("     call: the pool is lifespan infrastructure (03.9), and only work")
    print("     much bigger than the round-trip belongs in it (04.7)")


if __name__ == "__main__":
    shared_pool = concurrent.futures.ProcessPoolExecutor(max_workers=2)
    shared_pool.submit(int, 1).result()                 # warm it, like lifespan does
    try:
        asyncio.run(section_a(shared_pool))
        section_b()
        section_c(shared_pool)
    finally:
        shared_pool.shutdown()
