"""Lab for 04.1 The event loop inside a server process.

Reproduces the notebook's captures:
  A. one thread, many requests: tasks interleave at await points only
  B. the ready-queue law: loop lag grows linearly with (tasks × sync slice)
  C. asyncio's built-in detector: debug mode warning on an await-free stretch
  D. real server: big-page serialisation slices taxing a bystander /ping
     (starts uvicorn on port 8175, self-driving)

Run:  python lab_04_01_event_loop.py
"""
import asyncio
import logging
import statistics
import subprocess
import sys
import threading
import time
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel


# ---------- the app (used by section D's uvicorn subprocess) ----------------
class InvoiceRow(BaseModel):
    id: str
    customer: str
    total: str
    status: str
    created_at: str


ROW = InvoiceRow(id="inv_9f2c41", customer="cus_8f21ac", total="4200.00",
                 status="paid", created_at="2026-10-08T09:12:00Z")

app = FastAPI()


@app.get("/v1/reports/invoices", response_model=list[InvoiceRow])
async def report(limit: int = 200) -> list[InvoiceRow]:
    return [ROW] * limit          # serialisation of `limit` models: one sync slice


@app.get("/v1/ping")
async def ping() -> dict[str, bool]:
    return {"ok": True}


# ---------- A. interleaving on one thread -----------------------------------
async def section_a() -> None:
    print("A. one thread, three concurrent 'requests'")
    t0 = time.monotonic()

    def log(msg: str) -> None:
        print(f"  t={time.monotonic()-t0:4.2f}s [{threading.current_thread().name}] {msg}")

    async def handle(req: str) -> None:
        log(f"{req}: handler entered")
        await asyncio.sleep(0.05)                 # awaiting the DB (03.5's session)
        log(f"{req}: resumed after DB")
        await asyncio.sleep(0.05)                 # awaiting the tax API
        log(f"{req}: response ready")

    async with asyncio.TaskGroup() as tg:
        for r in ("req-1", "req-2", "req-3"):
            tg.create_task(handle(r))
    print("  => all three enter before any resumes: awaits are the ONLY yield points\n")


# ---------- B. the ready-queue law ------------------------------------------
def sync_slice(ms: float) -> None:
    end = time.perf_counter() + ms / 1000
    while time.perf_counter() < end:
        pass


async def measure_lag(n_tasks: int, slice_ms: float) -> float:
    """Sampler: how late does a 10ms sleep actually fire while n tasks each
    burn a sync slice between awaits?"""
    stop = time.monotonic() + 1.0
    lags: list[float] = []

    async def worker() -> None:
        while time.monotonic() < stop:
            sync_slice(slice_ms)                  # await-free stretch
            await asyncio.sleep(0)                # yield to the ready queue

    async def sampler() -> None:
        while time.monotonic() < stop:
            t0 = time.monotonic()
            await asyncio.sleep(0.01)
            lags.append((time.monotonic() - t0 - 0.01) * 1000)

    async with asyncio.TaskGroup() as tg:
        for _ in range(n_tasks):
            tg.create_task(worker())
        tg.create_task(sampler())
    return statistics.median(lags)


async def section_b() -> None:
    print("B. loop lag vs (concurrent tasks x 5ms sync slice each)")
    for n in (0, 4, 8, 16):
        lag = await measure_lag(n, 5.0)
        print(f"  {n:2d} tasks -> sampler's 10ms sleep fires {lag:6.1f} ms late")
    print("  => lag ~ queue depth x slice length: a tax added to EVERY request\n")


# ---------- C. the built-in detector ----------------------------------------
async def section_c() -> None:
    print("C. asyncio debug mode: the slow-callback warning")
    logging.basicConfig(level=logging.WARNING, format="  asyncio: %(message)s",
                        stream=sys.stdout)
    loop = asyncio.get_running_loop()
    loop.set_debug(True)
    loop.slow_callback_duration = 0.02            # budget: 20ms await-free max

    async def chunky() -> None:
        sync_slice(50)                            # a 50ms await-free stretch

    await asyncio.create_task(chunky())
    await asyncio.sleep(0)                        # let the warning flush
    loop.set_debug(False)
    print("  => the runtime names the exact task that overstayed its slice\n")


# ---------- D. real server: serialisation slices tax the bystander ----------
def section_d() -> None:
    import httpx

    print("D. uvicorn: /v1/ping p95 while 4 clients loop on the report endpoint")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "lab_04_01_event_loop:app", "--port", "8175"],
        cwd=Path(__file__).parent, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(40):
            try:
                httpx.get("http://127.0.0.1:8175/v1/ping", timeout=2)
                break
            except Exception:
                time.sleep(0.5)

        def ping_p95(label: str, report_limit: int | None) -> None:
            stop_flag = {"stop": False}

            def hammer() -> None:
                with httpx.Client(timeout=30) as hc:
                    while not stop_flag["stop"]:
                        hc.get(f"http://127.0.0.1:8175/v1/reports/invoices"
                               f"?limit={report_limit}")

            hammers = []
            if report_limit:
                hammers = [threading.Thread(target=hammer) for _ in range(4)]
                for h in hammers:
                    h.start()
                time.sleep(0.5)
            lat: list[float] = []
            with httpx.Client(timeout=30) as pc:
                for _ in range(60):
                    t0 = time.perf_counter()
                    pc.get("http://127.0.0.1:8175/v1/ping")
                    lat.append((time.perf_counter() - t0) * 1000)
                    time.sleep(0.02)
            stop_flag["stop"] = True
            for h in hammers:
                h.join()
            lat.sort()
            print(f"  {label:34} ping p50={lat[30]:6.1f} ms  p95={lat[57]:6.1f} ms")

        ping_p95("idle baseline", None)
        ping_p95("4 x /reports?limit=5000 looping", 5000)
        ping_p95("4 x /reports?limit=200 looping", 200)
        print("  => the report endpoint was never 'slow' — its serialisation slices")
        print("     queue in front of everyone else's awaits (04.1).")
    finally:
        proc.kill()


if __name__ == "__main__":
    asyncio.run(section_a())
    asyncio.run(section_b())
    asyncio.run(section_c())
    section_d()
