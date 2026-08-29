"""Lab for 04.2 Blocking vs non-blocking I/O — finding the blocking call.

Reproduces the notebook's captures:
  A. a real slow dependency called SYNC vs ASYNC: the bystander /ping freezes
     for the whole call in one case and doesn't notice in the other
     (uvicorn on 8177 calling a 2s "tax provider" on 8176)
  B. faulthandler.dump_traceback_later: the watchdog that names the exact
     stuck line while the loop is frozen
  C. what the 04.1 lag sampler sees during a freeze: silence, then one
     giant sample — the freeze measures itself on the way out
  D. the import guard: catching sync-I/O libraries in request-path modules

Run:  python lab_04_02_blocking.py
"""
import asyncio
import faulthandler
import http.server
import io
import threading
import time
import subprocess
import sys
from pathlib import Path

import httpx
from fastapi import FastAPI

PROVIDER_PORT, API_PORT = 8176, 8177


# ---------- the slow tax provider (a thread, 2s per answer) ------------------
class SlowProvider(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        time.sleep(2.0)                       # the provider's latency spike
        body = b'{"rate": "0.19"}'
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):                # quiet
        pass


def start_provider() -> http.server.ThreadingHTTPServer:
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", PROVIDER_PORT), SlowProvider)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


# ---------- the API under test (run as uvicorn subprocess for section A) -----
from contextlib import asynccontextmanager

SHARED_CLIENT: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 03.9's rule made mechanical: the client (and its one-time SSL-context
    # build) is constructed ONCE, at startup, off the request path
    SHARED_CLIENT["c"] = httpx.AsyncClient(timeout=5)
    yield
    await SHARED_CLIENT["c"].aclose()


app = FastAPI(lifespan=lifespan)


@app.get("/v1/rate-sync-async-def")
async def rate_sync_in_async() -> dict:
    """⚠️ the incident's shape: a SYNC client inside an ASYNC handler."""
    r = httpx.Client(timeout=5).get(f"http://127.0.0.1:{PROVIDER_PORT}/rate")
    return r.json()


@app.get("/v1/rate-async-per-request")
async def rate_async_per_request() -> dict:
    """⚠️ subtler: AsyncClient() PER REQUEST — its constructor builds an SSL
    context synchronously (cert-store load), a hidden slice on the loop."""
    async with httpx.AsyncClient(timeout=5) as c:
        r = await c.get(f"http://127.0.0.1:{PROVIDER_PORT}/rate")
    return r.json()


@app.get("/v1/rate-async-shared")
async def rate_async_shared() -> dict:
    r = await SHARED_CLIENT["c"].get(f"http://127.0.0.1:{PROVIDER_PORT}/rate")
    return r.json()


@app.get("/v1/ping")
async def ping() -> dict:
    return {"ok": True}


def section_a() -> None:
    print("A. bystander /ping while the handler waits on the 2s provider")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "lab_04_02_blocking:app",
         "--port", str(API_PORT)],
        cwd=Path(__file__).parent, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(40):
            try:
                httpx.get(f"http://127.0.0.1:{API_PORT}/v1/ping", timeout=2)
                break
            except Exception:
                time.sleep(0.5)

        # persistent clients: one-shot httpx.get builds a fresh SSL context per
        # call (~700ms of Windows cert-store loading) and poisons the timings
        ping_client = httpx.Client(timeout=10)
        rate_client = httpx.Client(timeout=10)
        rate_client.get(f"http://127.0.0.1:{API_PORT}/v1/rate-async-shared")  # warm
        t0 = time.perf_counter()
        ping_client.get(f"http://127.0.0.1:{API_PORT}/v1/ping")
        print(f"  idle baseline                     -> /v1/ping: "
              f"{(time.perf_counter()-t0)*1000:7.0f} ms")

        def probe(path: str) -> None:
            done = {}

            def call_rate() -> None:
                rate_client.get(f"http://127.0.0.1:{API_PORT}{path}")

            th = threading.Thread(target=call_rate)
            th.start()
            time.sleep(0.3)                                   # mid-call
            t0 = time.perf_counter()
            ping_client.get(f"http://127.0.0.1:{API_PORT}/v1/ping")
            done["ping_ms"] = (time.perf_counter() - t0) * 1000
            th.join()
            print(f"  {path:33} -> /v1/ping during the call: {done['ping_ms']:7.0f} ms")

        probe("/v1/rate-async-shared")
        probe("/v1/rate-async-per-request")
        probe("/v1/rate-sync-async-def")
        print("  => shared client, awaited: the loop serves everyone while parked.")
        print("     AsyncClient PER REQUEST: 'async' code hiding a sync SSL-context")
        print("     build on the loop. Sync client in async def: the loop is GONE")
        print("     for the whole provider call (04.2).\n")
    finally:
        proc.kill()


# ---------- B. the watchdog that names the line ------------------------------
def section_b() -> None:
    print("B. faulthandler.dump_traceback_later: naming the stuck line")
    import tempfile

    tmp = tempfile.NamedTemporaryFile(mode="w+", suffix=".dump", delete=False)
    faulthandler.dump_traceback_later(1.0, file=tmp, exit=False)

    async def frozen_handler() -> None:
        httpx.Client(timeout=5).get(f"http://127.0.0.1:{PROVIDER_PORT}/rate")

    asyncio.run(frozen_handler())
    faulthandler.cancel_dump_traceback_later()
    tmp.seek(0)
    dump = tmp.read()
    tmp.close()
    # keep the MAIN thread's block — the frozen event loop — not the helpers
    # 3.14 labels blocks only "Thread 0x... (most recent call first):"; the
    # main thread — our frozen loop — is the LAST block in the dump
    blocks: list[list[str]] = []
    for line in dump.splitlines():
        if line.startswith("Thread 0x"):
            blocks.append([])
        elif blocks and "File" in line:
            blocks[-1].append(line.strip())
    lines = ["Timeout (0:00:01)!  ...  Thread 0x… (the frozen event loop):"]
    lines += blocks[-1][:5] if blocks else ["<no dump captured>"]
    print("  watchdog fired at t=1.0s while the loop was frozen; the dump says:")
    for l in lines:
        print("   ", l.strip())
    print("  => the exact frame the worker is stuck in, from stdlib alone (04.2)\n")


# ---------- C. what the sampler sees -----------------------------------------
def section_c() -> None:
    print("C. the 04.1 lag sampler during a freeze")
    samples: list[tuple[float, float]] = []

    async def main() -> None:
        t_start = time.monotonic()

        async def sampler() -> None:
            while time.monotonic() - t_start < 3.5:
                t0 = time.monotonic()
                await asyncio.sleep(0.25)
                lag = (time.monotonic() - t0 - 0.25) * 1000
                samples.append((time.monotonic() - t_start, lag))

        task = asyncio.create_task(sampler())
        await asyncio.sleep(0.6)
        httpx.Client(timeout=5).get(f"http://127.0.0.1:{PROVIDER_PORT}/rate")  # freeze
        await task

    asyncio.run(main())
    for t, lag in samples:
        bar = "#" * min(60, int(lag / 40))
        print(f"  t={t:4.1f}s  lag={lag:7.1f} ms {bar}")
    print("  => silence during the freeze, then ONE giant sample: the metric")
    print("     reports the freeze only after it ends — gaps ARE the signal (04.2)\n")


# ---------- D. the import guard ----------------------------------------------
BANNED_SYNC_IO = {"requests", "urllib3", "boto3", "smtplib", "psycopg2"}


def section_d() -> None:
    print("D. the import guard on request-path modules")
    fake_module_imports = {
        "ledgerly/routers/invoices.py": {"fastapi", "ledgerly.services"},
        "ledgerly/services/tax.py": {"httpx", "ledgerly.schemas"},
        "ledgerly/services/tax_vendor_sdk.py": {"requests", "urllib3"},   # the culprit
    }
    for module, imports in fake_module_imports.items():
        hits = imports & BANNED_SYNC_IO
        verdict = f"FAIL — sync I/O import(s): {sorted(hits)}" if hits else "ok"
        print(f"  {module:40} {verdict}")
    print("  => mocks hide runtime blocking in CI; imports don't lie (04.2)")


if __name__ == "__main__":
    provider = start_provider()
    try:
        section_a()
        section_b()
        section_c()
        section_d()
    finally:
        provider.shutdown()
