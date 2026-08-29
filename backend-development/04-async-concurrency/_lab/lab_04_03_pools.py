"""Lab for 04.3 Async database and HTTP clients — pools and limits.

Reproduces the notebook's captures:
  A. httpx pool exhaustion: max_connections=5, pool timeout 1s, 8 concurrent
     calls to a slow dependency -> 5 proceed, 3 fail fast with PoolTimeout
  B. head-of-line on ONE shared client: a healthy 50ms dependency starves
     behind a degraded 2s dependency; per-dependency clients fix it
  C. the defaults you are silently running on (httpx Limits/Timeout)
  D. SQLAlchemy's pool at exhaustion: the canonical QueuePool TimeoutError

Run:  python lab_04_03_pools.py     (in-process; a threaded provider on 8178)
"""
import asyncio
import http.server
import threading
import time

import httpx

PORT = 8178


# ---------- one provider, two dependencies -----------------------------------
class Provider(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        time.sleep(2.0 if self.path.startswith("/render") else 0.05)
        body = b'{"ok": true}'
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


def start_provider() -> http.server.ThreadingHTTPServer:
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Provider)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


# ---------- A. exhaustion, measured ------------------------------------------
async def section_a() -> None:
    print("A. max_connections=5, pool timeout=1s, 8 concurrent 2s calls")
    limits = httpx.Limits(max_connections=5, max_keepalive_connections=5)
    timeout = httpx.Timeout(5.0, pool=1.0)          # wait ≤1s for a connection
    outcomes: list[str] = []

    async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
        async def call(i: int) -> None:
            t0 = time.monotonic()
            try:
                await client.get(f"http://127.0.0.1:{PORT}/render")
                outcomes.append(f"OK after {time.monotonic()-t0:.1f}s")
            except httpx.PoolTimeout:
                outcomes.append(f"PoolTimeout after {time.monotonic()-t0:.1f}s")

        async with asyncio.TaskGroup() as tg:
            for i in range(8):
                tg.create_task(call(i))

    for line in sorted(outcomes):
        print("  ", line)
    print("  => 5 borrowed the pool for 2s; the other 3 failed FAST at the pool")
    print("     timeout instead of camping — exhaustion is a designed outcome (04.3)\n")


# ---------- B. shared client vs per-dependency clients -----------------------
async def tax_latency_while_renderer_degraded(shared: bool) -> str:
    limits = httpx.Limits(max_connections=5, max_keepalive_connections=5)
    timeout = httpx.Timeout(5.0, pool=1.0)

    if shared:
        one = httpx.AsyncClient(limits=limits, timeout=timeout)
        renderer_client = tax_client = one
    else:
        renderer_client = httpx.AsyncClient(limits=limits, timeout=timeout)
        tax_client = httpx.AsyncClient(limits=limits, timeout=timeout)

    async def render_send() -> None:                 # background load: failures are its own
        try:
            await renderer_client.get(f"http://127.0.0.1:{PORT}/render")
        except httpx.HTTPError:
            pass

    try:
        async with asyncio.TaskGroup() as tg:
            for _ in range(5):                       # invoice sends saturate the pool
                tg.create_task(render_send())
            await asyncio.sleep(0.2)                 # mid-degradation, a tax call:
            t0 = time.monotonic()
            try:
                await tax_client.get(f"http://127.0.0.1:{PORT}/rate")
                return f"tax call OK in {(time.monotonic()-t0)*1000:6.0f} ms"
            except httpx.PoolTimeout:
                return f"tax call PoolTimeout after {time.monotonic()-t0:.1f}s"
    finally:
        await renderer_client.aclose()
        if not shared:
            await tax_client.aclose()


async def section_b() -> None:
    print("B. a healthy 50ms tax dependency while the renderer runs at 2s")
    print("   ONE shared client  :", await tax_latency_while_renderer_degraded(True))
    print("   per-dependency     :", await tax_latency_while_renderer_degraded(False))
    print("  => on the shared client the tax call queued behind renderer holds and")
    print("     died at the pool — its own dependency was healthy the whole time.")
    print("     A client per dependency is a bulkhead (02.11, 04.3)\n")


# ---------- C. the defaults ---------------------------------------------------
def section_c() -> None:
    from httpx._config import DEFAULT_LIMITS, DEFAULT_TIMEOUT_CONFIG

    print("C. what you run on when you configure nothing")
    print(f"   AsyncClient() limits : {DEFAULT_LIMITS}")
    print(f"   AsyncClient() timeout: {DEFAULT_TIMEOUT_CONFIG}  (per phase, incl. pool)")
    print("  => 100 connections shared by every dependency behind one client, and")
    print("     a 5s silent queue at the pool before anything errors (04.3)\n")


# ---------- D. the database pool at exhaustion --------------------------------
def section_d() -> None:
    import tempfile
    from sqlalchemy import create_engine, text

    print("D. SQLAlchemy QueuePool: pool_size=2, max_overflow=1, pool_timeout=1")
    db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db.close()
    engine = create_engine(f"sqlite:///{db.name}", pool_size=2, max_overflow=1,
                           pool_timeout=1)
    held = [engine.connect() for _ in range(3)]      # size 2 + overflow 1: all out
    print(f"   3 connections held; pool status: {engine.pool.status()}")
    t0 = time.monotonic()
    try:
        engine.connect()
    except Exception as e:
        print(f"   4th checkout after {time.monotonic()-t0:.1f}s ->")
        print(f"     {type(e).__name__}: {e}")
    for c in held:
        c.close()
    engine.dispose()
    print("  => the same borrow/queue/timeout life as httpx's pool — one mental")
    print("     model for every connection pool you own (04.3)")


if __name__ == "__main__":
    provider = start_provider()
    try:
        asyncio.run(section_a())
        asyncio.run(section_b())
        section_c()
        section_d()
    finally:
        provider.shutdown()
