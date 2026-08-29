"""Lab for 01.1 Request/response lifecycle.

Reproduces the incident's mechanism: ONE blocking call inside an `async def`
handler stalls the event loop, so every other request queues behind it — while
a properly awaited version overlaps. The wall-clock numbers are the proof.

Run:  python lab_01_01_lifecycle.py     (starts uvicorn on port 8161, self-driving)
"""
import asyncio
import subprocess
import sys
import threading
import time
from pathlib import Path

from fastapi import FastAPI

app = FastAPI()


@app.get("/v1/invoices/pdf-blocking")
async def pdf_blocking() -> dict[str, str]:
    time.sleep(1.0)                    # the sync PDF render inside async def
    return {"pdf": "rendered"}


@app.get("/v1/invoices/pdf-awaited")
async def pdf_awaited() -> dict[str, str]:
    await asyncio.sleep(1.0)           # same latency, but the loop keeps serving
    return {"pdf": "rendered"}


@app.get("/v1/ping")
async def ping() -> dict[str, bool]:
    return {"ok": True}


def drive() -> None:
    import httpx

    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "lab_01_01_lifecycle:app", "--port", "8161"],
        cwd=Path(__file__).parent, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(40):
            try:
                httpx.get("http://127.0.0.1:8161/v1/ping", timeout=2)
                break
            except Exception:
                time.sleep(0.5)

        def fire(path: str, n: int = 3) -> float:
            t0 = time.monotonic()
            threads = [threading.Thread(target=httpx.get,
                                        args=(f"http://127.0.0.1:8161{path}",),
                                        kwargs={"timeout": 30}) for _ in range(n)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            return time.monotonic() - t0

        print(f"3 concurrent GET /pdf-awaited  (1s each): {fire('/v1/invoices/pdf-awaited'):.1f}s total")
        print(f"3 concurrent GET /pdf-blocking (1s each): {fire('/v1/invoices/pdf-blocking'):.1f}s total")

        # and what an innocent bystander experiences while ONE blocking call runs:
        bystander = {}
        t = threading.Thread(target=lambda: httpx.get(
            "http://127.0.0.1:8161/v1/invoices/pdf-blocking", timeout=30))
        t.start()
        time.sleep(0.1)
        t0 = time.monotonic()
        httpx.get("http://127.0.0.1:8161/v1/ping", timeout=30)
        bystander["latency"] = time.monotonic() - t0
        t.join()
        print(f"GET /v1/ping while a blocking render runs: {bystander['latency']*1000:.0f} ms "
              "(should be ~1 ms)")
        print("\n=> one sync call inside async def serialises the whole worker; the")
        print("   app's own histogram never sees the queueing in front of it (01.1).")
    finally:
        proc.kill()


if __name__ == "__main__":
    drive()
