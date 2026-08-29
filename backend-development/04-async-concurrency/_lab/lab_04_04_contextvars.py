"""Lab for 04.4 Request-scoped state — contextvars.

Reproduces the notebook's captures:
  A. the bleed: threading.local under interleaving tasks mislabels tenants;
     ContextVar stays correct — measured over 40 concurrent "requests"
  B. inheritance: a task created mid-request snapshots the context at
     creation; later writes in the parent are invisible to it
  C. propagation into threads: loop.run_in_executor does NOT carry context;
     anyio.to_thread.run_sync (what Starlette runs def endpoints with) DOES
  D. real server: interleaved concurrent requests each log their own
     request id via ContextVar while a thread-local column goes wrong;
     plus: does a set-without-reset leak into the next request on the
     same keep-alive connection?  (uvicorn on port 8179)

Run:  python lab_04_04_contextvars.py
"""
import asyncio
import contextvars
import subprocess
import sys
import threading
import time
from pathlib import Path

import anyio.to_thread
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

tenant_local = threading.local()
tenant_var: contextvars.ContextVar[str] = contextvars.ContextVar("tenant", default="-")


# ---------- A. the bleed, measured -------------------------------------------
async def section_a() -> None:
    print("A. 40 interleaving 'requests': who does each one think it is?")
    wrong = {"local": 0, "ctxvar": 0}

    async def request(tenant: str) -> None:
        tenant_local.value = tenant                 # the Flask-era helper
        token = tenant_var.set(tenant)              # the async-native one
        await asyncio.sleep(0.001)                  # any await: others run here
        if tenant_local.value != tenant:
            wrong["local"] += 1
        if tenant_var.get() != tenant:
            wrong["ctxvar"] += 1
        tenant_var.reset(token)

    async with asyncio.TaskGroup() as tg:
        for i in range(40):
            tg.create_task(request(f"t_{i:03d}"))

    print(f"   threading.local wrong after one await: {wrong['local']}/40")
    print(f"   ContextVar      wrong after one await: {wrong['ctxvar']}/40")
    print("  => one thread serves every task (04.1): a thread-local is GLOBAL")
    print("     here; each task runs in its own copied Context (04.4)\n")


# ---------- B. inheritance is a snapshot -------------------------------------
async def section_b() -> None:
    print("B. a task created mid-request snapshots the context")
    seen: dict[str, str] = {}

    async def child() -> None:
        await asyncio.sleep(0.01)
        seen["child sees"] = tenant_var.get()

    token = tenant_var.set("t_44f1")
    task = asyncio.create_task(child())             # snapshot taken HERE
    tenant_var.set("t_9999")                        # parent moves on
    seen["parent now"] = tenant_var.get()
    await task
    tenant_var.reset(token)
    print(f"   parent set t_44f1, spawned child, then set t_9999")
    print(f"   child sees: {seen['child sees']}   parent now: {seen['parent now']}")
    print("  => create_task copies the context at CREATION: children keep the")
    print("     request identity they were born under — and keep it alive (04.4)\n")


# ---------- C. propagation into threads --------------------------------------
async def section_c() -> None:
    print("C. does the context survive into a worker thread?")
    token = tenant_var.set("t_44f1")
    loop = asyncio.get_running_loop()

    def read_in_thread() -> str:
        return tenant_var.get()

    via_executor = await loop.run_in_executor(None, read_in_thread)
    via_anyio = await anyio.to_thread.run_sync(read_in_thread)
    tenant_var.reset(token)
    print(f"   loop.run_in_executor(...)     sees: {via_executor!r}")
    print(f"   anyio.to_thread.run_sync(...) sees: {via_anyio!r}   "
          "(what def endpoints use, 03.6)")
    print("  => raw executor calls lose the context (wrap in copy_context().run);")
    print("     Starlette's def-endpoint path carries it for you (04.4)\n")


# ---------- D. the server proof ----------------------------------------------
app = FastAPI()
req_local = threading.local()
req_var: contextvars.ContextVar[str] = contextvars.ContextVar("req", default="-")
LOG: list[str] = []


class RequestContextMiddleware(BaseHTTPMiddleware):
    """03.7's outermost middleware, mechanism revealed — WITHOUT reset, for
    the keep-alive leak probe (the real one resets in finally; see 04.4)."""

    async def dispatch(self, request, call_next):
        rid = request.headers.get("x-request-id")
        if rid is not None:                         # /v1/peek sends none: it only READS
            req_local.value = rid
            req_var.set(rid)                        # deliberately no reset here
        return await call_next(request)


app.add_middleware(RequestContextMiddleware)


@app.get("/v1/work")
async def work(request: Request) -> dict[str, str]:
    await asyncio.sleep(0.3)                        # interleave point
    line = (f"handled rid={request.headers['x-request-id']:>5} | "
            f"ctxvar={req_var.get():>5} | thread_local="
            f"{getattr(req_local, 'value', '-'):>5}")
    print(line, flush=True)
    return {"ok": rid_ok(request)}


@app.get("/v1/peek")
async def peek() -> dict[str, str]:
    """What does a request that SETS nothing see? (keep-alive leak probe)"""
    return {"ctxvar": req_var.get(), "thread_local": getattr(req_local, "value", "-")}


def rid_ok(request: Request) -> str:
    return str(req_var.get() == request.headers.get("x-request-id"))


def section_d() -> None:
    import httpx

    print("D. real server: interleaved requests, and the keep-alive leak probe")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "lab_04_04_contextvars:app",
         "--port", "8179", "--log-level", "warning"],
        cwd=Path(__file__).parent, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8",
    )
    lines: list[str] = []
    threading.Thread(target=lambda: [lines.append(l.rstrip()) for l in proc.stdout],
                     daemon=True).start()
    try:
        client = httpx.Client(timeout=10)
        for _ in range(40):
            try:
                client.get("http://127.0.0.1:8179/v1/peek")
                break
            except Exception:
                time.sleep(0.5)

        threads = [threading.Thread(
            target=lambda i=i: httpx.Client(timeout=10).get(
                "http://127.0.0.1:8179/v1/work",
                headers={"x-request-id": f"r_{i:03d}"}))
            for i in range(6)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        time.sleep(0.3)
        for l in lines:
            if "handled" in l:
                print("  ", l)

        # keep-alive leak probe: same connection, /work sets vars, /peek sets none
        r1 = client.get("http://127.0.0.1:8179/v1/work",
                        headers={"x-request-id": "r_AAA"})
        r2 = client.get("http://127.0.0.1:8179/v1/peek")
        print(f"   same keep-alive connection, next request (sets nothing):")
        print(f"     /v1/peek sees: {r2.json()}")
        print("  => six interleaved requests: the ContextVar column is always right,")
        print("     the thread-local column is whoever wrote LAST. The leak probe")
        print("     shows what set-without-reset leaves behind (04.4).")
    finally:
        proc.kill()


if __name__ == "__main__":
    asyncio.run(section_a())
    asyncio.run(section_b())
    asyncio.run(section_c())
    section_d()
