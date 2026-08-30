"""Lab for 04.8 Timeouts and cancellation.

Reproduces the notebook's captures:
  A. cancellation anatomy: CancelledError lands at the await; finally runs;
     a swallowed cancel makes the task refuse to die (03.9's lore, measured)
  B. asyncio.timeout(): CancelledError inside the block, TimeoutError at
     its edge — the conversion, layer by layer
  C. cancellation cannot reach sync code: the await raises immediately,
     the executor thread finishes its work anyway (zombie work)
  D. the single-flight promise (04.5): cancelling a WAITER leaves the shared
     task alive; asyncio.wait_for CANCELS the task it wraps — measured both
  E. real server: does a client disconnect cancel the running handler?
     (uvicorn on 8180 — the pinned stack answers, not folklore)
  F. shield: the critical section survives the outer timeout

Run:  python lab_04_08_cancellation.py
"""
import asyncio
import subprocess
import sys
import threading
import time
from pathlib import Path

from fastapi import FastAPI, Request

# Windows: a redirected/piped stdout falls back to cp1252, which cannot encode
# this script's ⚠️ marker and kills section D mid-print — force UTF-8 output
if sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ---------- A. anatomy --------------------------------------------------------
async def section_a() -> None:
    print("A. where cancellation lands, and the task that refuses to die")
    events: list[str] = []

    async def polite() -> None:
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            events.append("polite: CancelledError AT the await")
            raise
        finally:
            events.append("polite: finally ran (cleanup happens)")

    task = asyncio.create_task(polite())
    await asyncio.sleep(0.05)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        events.append("caller: task is cancelled")
    for e in events:
        print("  ", e)

    stop = asyncio.Event()                             # lab-only escape hatch

    async def swallower() -> None:
        while not stop.is_set():
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                pass                                   # ⚠️ 03.9's sin, measured

    z = asyncio.create_task(swallower())
    await asyncio.sleep(0.05)
    z.cancel()
    done, _ = await asyncio.wait([z], timeout=0.3)
    print(f"   swallower: cancel() sent, waited 300ms — task finished? {bool(done)}")
    z.cancel()
    await asyncio.sleep(0.05)
    print(f"   swallower: second cancel — done now? {z.done()}")
    stop.set(); z.cancel()                              # only the escape hatch works
    await asyncio.wait([z], timeout=0.5)
    print("  => swallow the CancelledError and shutdown waits forever on a task")
    print("     that cannot be killed politely — re-raise, always (03.9, 04.8)\n")


# ---------- B. timeout conversion ---------------------------------------------
async def section_b() -> None:
    print("B. asyncio.timeout(): what each layer sees")

    async def inner() -> None:
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            print("   inner : CancelledError (the mechanism is cancellation)")
            raise

    try:
        async with asyncio.timeout(0.1):
            await inner()
    except TimeoutError:
        print("   outer : TimeoutError (converted at the block edge)")
    print("  => one mechanism, two faces: inside the deadline it is a cancel")
    print("     to clean up after; at the boundary it becomes the verdict (04.8)\n")


# ---------- C. sync code is unreachable ---------------------------------------
def section_c_sync_work(marker: dict) -> None:
    time.sleep(1.0)
    marker["thread_finished_at"] = time.monotonic()


async def section_c() -> None:
    print("C. cancelling work that is inside a sync call (04.2/04.7's homes)")
    marker: dict = {}
    loop = asyncio.get_running_loop()
    t0 = time.monotonic()

    async def uses_executor() -> None:
        await loop.run_in_executor(None, section_c_sync_work, marker)

    task = asyncio.create_task(uses_executor())
    await asyncio.sleep(0.2)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print(f"   await raised CancelledError at t={time.monotonic()-t0:.1f}s")
    await asyncio.sleep(1.0)
    print(f"   ...but the THREAD finished its work at "
          f"t={marker['thread_finished_at']-t0:.1f}s anyway")
    print("  => cancellation frees the AWAITER; the sync work is a zombie that")
    print("     completes — and its side effects land — regardless (04.8)\n")


# ---------- D. waiters vs wrappers --------------------------------------------
async def section_d() -> None:
    print("D. what a cancelled waiter does to the shared flight (04.5's cache)")

    def make_flight() -> tuple[asyncio.Task, list[str]]:
        result: list[str] = []

        async def refresh() -> str:
            await asyncio.sleep(0.3)
            result.append("token issued")
            return "tok_001"

        return asyncio.create_task(refresh()), result

    # naive: the waiter awaits the Task directly (04.5's TokenCache as written)
    flight, result = make_flight()

    async def naive_waiter() -> None:
        await flight

    w = asyncio.create_task(naive_waiter())
    await asyncio.sleep(0.05)
    w.cancel()
    await asyncio.sleep(0.4)
    print(f"   naive await  : waiter cancelled -> flight.cancelled()="
          f"{flight.cancelled()}  issued={result}")

    # shielded: the waiter's deadline is its own; the flight is everyone's
    flight2, result2 = make_flight()

    async def shielded_waiter() -> None:
        await asyncio.shield(flight2)

    w2 = asyncio.create_task(shielded_waiter())
    await asyncio.sleep(0.05)
    w2.cancel()
    await asyncio.sleep(0.4)
    print(f"   shielded     : waiter cancelled -> flight.cancelled()="
          f"{flight2.cancelled()}  issued={result2}")

    # wait_for: explicitly a kill-switch for what it wraps
    flight3, result3 = make_flight()
    try:
        await asyncio.wait_for(flight3, timeout=0.05)
    except TimeoutError:
        pass
    await asyncio.sleep(0.4)
    print(f"   wait_for     : timeout        -> flight.cancelled()="
          f"{flight3.cancelled()}  issued={result3}")
    print("  => ⚠️ cancelling a task CANCELS whatever future it is awaiting —")
    print("     a naive `await shared_task` lets one impatient waiter kill the")
    print("     flight for everyone. Waiters shield; wait_for is a kill-switch")
    print("     by design (04.5 amended, 04.8)\n")


# ---------- E. the real server answers ----------------------------------------
app = FastAPI()
COMPLETED = {"blind": 0, "aware": 0}


@app.get("/v1/render-blind")
async def render_blind() -> dict:
    await asyncio.sleep(1.5)                           # the expensive render
    COMPLETED["blind"] += 1                            # side effect at the end
    return {"rendered": True}


@app.get("/v1/render-aware")
async def render_aware(request: Request) -> dict:
    for _ in range(15):
        await asyncio.sleep(0.1)
        if await request.is_disconnected():
            return {"aborted": True}                   # stop paying for nobody
    COMPLETED["aware"] += 1
    return {"rendered": True}


@app.get("/v1/completed")
async def completed() -> dict:
    return COMPLETED


def section_e() -> None:
    import httpx

    print("E. the client hangs up at t=0.3s of a 1.5s handler — does work stop?")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "lab_04_08_cancellation:app",
         "--port", "8180", "--log-level", "warning"],
        cwd=Path(__file__).parent, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        client = httpx.Client(timeout=10)
        for _ in range(40):
            try:
                client.get("http://127.0.0.1:8180/v1/completed")
                break
            except Exception:
                time.sleep(0.5)

        for path in ("render-blind", "render-aware"):
            try:
                httpx.get(f"http://127.0.0.1:8180/v1/{path}", timeout=0.3)
            except httpx.TimeoutException:
                pass                                   # client gave up: disconnect
        time.sleep(2.5)                                # give handlers time to finish
        counts = client.get("http://127.0.0.1:8180/v1/completed").json()
        print(f"   completed side effects after both disconnects: {counts}")
        print("  => on this stack the abandoned handler RUNS TO COMPLETION —")
        print("     no cancellation on disconnect; the response is written to a")
        print("     dead socket. Awareness (is_disconnected) is opt-in (04.8).")
    finally:
        proc.kill()


# ---------- F. shield ---------------------------------------------------------
async def section_f() -> None:
    print("\nF. shield: the critical section outlives the deadline")
    state: list[str] = []

    async def commit_like() -> None:
        await asyncio.sleep(0.3)
        state.append("critical section completed")

    try:
        async with asyncio.timeout(0.1):
            await asyncio.shield(commit_like())
    except TimeoutError:
        print("   caller: TimeoutError at t=0.1s (gave up waiting)")
    await asyncio.sleep(0.4)
    print(f"   shielded work: {state}")
    print("  => shield decouples the waiter's deadline from the work's fate —")
    print("     for the rare op that must not be half-done; prefer transactions (04.6)")


if __name__ == "__main__":
    asyncio.run(section_a())
    asyncio.run(section_b())
    asyncio.run(section_c())
    asyncio.run(section_d())
    section_e()
    asyncio.run(section_f())
