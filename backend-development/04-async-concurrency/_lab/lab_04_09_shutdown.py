"""Lab for 04.9 Graceful shutdown.

Reproduces the notebook's captures:
  A. drain ORDER decides data loss: naively cancelling a queue's writer task
     loses the queued items; stop-intake -> flush -> cancel loses zero
  B. teardown must mirror startup: closing the shared client BEFORE the task
     that uses it turns the last flush into an error; reverse order is clean
  C. the drain helper that escalates: cancel, wait briefly, NAME the task
     that refused (04.8's swallower, met at shutdown)
  D. the zombie thread delays exit: asyncio.run() cannot return until the
     default executor's threads finish (04.8's zombie, met at shutdown)

Run:  python lab_04_09_shutdown.py     (pure asyncio; no server)
"""
import asyncio
import time


# ---------- A. drain order = data loss or not --------------------------------
async def run_pipeline(*, ordered: bool) -> tuple[int, int]:
    queue: asyncio.Queue[int] = asyncio.Queue(maxsize=64)
    written: list[int] = []
    produced = {"n": 0}

    async def producer() -> None:          # requests enqueueing audit events
        try:
            while True:
                produced["n"] += 1
                await queue.put(produced["n"])
                await asyncio.sleep(0.005)
        except asyncio.CancelledError:
            raise

    async def writer() -> None:            # the batching writer task
        try:
            while True:
                item = await queue.get()
                await asyncio.sleep(0.02)  # the batched INSERT
                written.append(item)
                queue.task_done()
        except asyncio.CancelledError:
            raise

    prod = asyncio.create_task(producer())
    wr = asyncio.create_task(writer())
    await asyncio.sleep(0.4)               # the process serves traffic...

    if ordered:                            # ...then SIGTERM arrives:
        prod.cancel()                      # 1. stop intake FIRST
        await asyncio.gather(prod, return_exceptions=True)
        await queue.join()                 # 2. let the writer flush the queue
        wr.cancel()                        # 3. only then cancel the writer
        await asyncio.gather(wr, return_exceptions=True)
    else:
        for t in (prod, wr):               # naive: cancel everything at once
            t.cancel()
        await asyncio.gather(prod, wr, return_exceptions=True)

    return produced["n"], len(written)


async def section_a() -> None:
    print("A. deploy arrives while the audit queue is busy")
    for ordered in (False, True):
        n, w = await run_pipeline(ordered=ordered)
        label = "ordered drain " if ordered else "naive cancel  "
        print(f"   {label}: produced={n:3d}  written={w:3d}  LOST={n - w}")
    print("  => cancellation order IS the data-loss policy: stop intake, flush,")
    print("     then cancel — or every deploy quietly deletes a queue (04.9)\n")


# ---------- B. teardown mirrors startup --------------------------------------
class FakeClient:
    def __init__(self) -> None:
        self.closed = False

    async def send(self, item: str) -> None:
        if self.closed:
            raise RuntimeError("client is closed")
        await asyncio.sleep(0.01)

    async def aclose(self) -> None:
        self.closed = True


async def run_teardown(*, mirror: bool) -> str:
    client = FakeClient()                                  # startup: client FIRST
    outcome = {"final_flush": "?"}

    async def flusher() -> None:                           # startup: task SECOND
        try:
            while True:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            try:
                await client.send("final flush")           # last duty on the way out
                outcome["final_flush"] = "delivered"
            except RuntimeError as e:
                outcome["final_flush"] = f"FAILED ({e})"
            raise

    task = asyncio.create_task(flusher())
    await asyncio.sleep(0.05)

    if mirror:                                             # reverse of startup:
        task.cancel()                                      # task first...
        await asyncio.gather(task, return_exceptions=True)
        await client.aclose()                              # ...client last
    else:
        await client.aclose()                              # ❌ client first
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
    return outcome["final_flush"]


async def section_b() -> None:
    print("B. the flusher's last duty vs teardown order")
    print(f"   close client, then cancel task : final flush {await run_teardown(mirror=False)}")
    print(f"   cancel task, then close client : final flush {await run_teardown(mirror=True)}")
    print("  => teardown mirrors startup in reverse (03.9) because dependencies")
    print("     point backwards: the task's dying breath needs the client alive (04.9)\n")


# ---------- C. the escalating drain helper -----------------------------------
async def drain(tasks: dict[str, asyncio.Task], grace: float = 0.3) -> list[str]:
    """Cancel everything, wait briefly, name whatever refused (04.9)."""
    for t in tasks.values():
        t.cancel()
    await asyncio.wait(set(tasks.values()), timeout=grace)
    return [name for name, t in tasks.items() if not t.done()]


async def section_c() -> None:
    print("C. drain with escalation: who refused to die?")

    stop = asyncio.Event()

    async def polite_sampler() -> None:
        await asyncio.sleep(3600)                          # re-raises by default

    async def legacy_poller() -> None:                     # 04.8's swallower
        while not stop.is_set():
            try:
                await asyncio.sleep(3600)
            except asyncio.CancelledError:
                pass                                       # ⚠️ the sin, again

    tasks = {"loop_lag_sampler": asyncio.create_task(polite_sampler()),
             "legacy_poller": asyncio.create_task(legacy_poller())}
    await asyncio.sleep(0.05)
    stuck = await drain(tasks)
    print(f"   drained politely: {[n for n in tasks if n not in stuck]}")
    print(f"   REFUSED cancellation after grace: {stuck}")
    stop.set(); tasks["legacy_poller"].cancel()
    await asyncio.wait(set(tasks.values()), timeout=0.5)
    print("  => a drain that cannot name its hostage-taker becomes 03.14's")
    print("     mystery hang; log the names, then let the guillotine work (04.9)\n")


# ---------- D. the zombie thread holds the exit ------------------------------
def section_d() -> None:
    print("D. asyncio.run() vs a thread still working at shutdown")

    async def main() -> None:
        loop = asyncio.get_running_loop()
        loop.run_in_executor(None, time.sleep, 1.2)        # fire-and-forget (⚠️)
        await asyncio.sleep(0.1)                           # "shutdown" reached

    t0 = time.monotonic()
    asyncio.run(main())
    print(f"   coroutine finished at ~0.1s; asyncio.run returned after "
          f"{time.monotonic()-t0:.1f}s")
    print("  => run() waits for the default executor's threads: every zombie")
    print("     (04.8) is borrowed drain-deadline; 03.14's guillotine does not")
    print("     wait with you (04.9)")


if __name__ == "__main__":
    asyncio.run(section_a())
    asyncio.run(section_b())
    asyncio.run(section_c())
    section_d()
