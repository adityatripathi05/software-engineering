"""Lab for 02.11 Webhook design.

Reproduces the head-of-line incident with real concurrency: destination B
accepts connections and never answers (each delivery burns a worker for the
full timeout); with one SHARED worker pool, healthy destination A's delivery
lag climbs to seconds. Per-destination bulkheads cap B's damage at its own
allotment and A stays fast. Timings are measured, not asserted.
"""
import asyncio
import time

TIMEOUT = 0.5          # the 5s delivery timeout, scaled 10x down
EVENTS = 30            # mixed queue: A and the dead B interleaved


async def deliver(dest: str) -> None:
    if dest == "B":
        await asyncio.sleep(TIMEOUT)          # hangs until timeout
    else:
        await asyncio.sleep(0.01)             # healthy receiver


async def run(shared: bool) -> dict[str, float]:
    t0 = time.monotonic()
    lags: dict[str, list[float]] = {"A": [], "B": []}

    async def worker(queue: asyncio.Queue) -> None:
        while True:
            try:
                dest = queue.get_nowait()
            except asyncio.QueueEmpty:
                return
            await deliver(dest)
            lags[dest].append(time.monotonic() - t0)

    if shared:
        q: asyncio.Queue[str] = asyncio.Queue()
        for i in range(EVENTS):
            q.put_nowait("B" if i % 2 else "A")             # one FIFO, any worker
        await asyncio.gather(*(worker(q) for _ in range(4)))
    else:
        qa: asyncio.Queue[str] = asyncio.Queue()            # per-destination queues
        qb: asyncio.Queue[str] = asyncio.Queue()            # with DEDICATED workers
        for i in range(EVENTS):
            (qb if i % 2 else qa).put_nowait("B" if i % 2 else "A")
        await asyncio.gather(worker(qa), worker(qa), worker(qb), worker(qb))
    return {d: max(v) for d, v in lags.items() if v}


async def main() -> None:
    shared = await run(shared=True)
    print(f"SHARED pool of 4 workers, dest B hanging (timeout {TIMEOUT}s):")
    print(f"  worst delivery lag — healthy A: {shared['A']:.2f}s   dead B: {shared['B']:.2f}s")
    print("  => A's events queue behind B's doomed timeouts: workers have no")
    print("     concept of a destination (02.11)\n")

    isolated = await run(shared=False)
    print("PER-DESTINATION bulkheads (2 slots each), same traffic:")
    print(f"  worst delivery lag — healthy A: {isolated['A']:.2f}s   dead B: {isolated['B']:.2f}s")
    print("\n=> B still burns ITS slots; A never waits behind them. One hanging")
    print("   receiver cost 187 of 200 shared workers — bulkheads cap it at its")
    print("   own allotment (02.11).")


asyncio.run(main())
