"""Lab for 03.6 Sync vs async endpoints.

Reproduces: def endpoints run on the shared anyio threadpool (default 40 tokens —
the budget the incident's arithmetic uses), async endpoints run on the event
loop, and the pool is one budget for the whole process.
"""
import threading

import anyio.to_thread
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


@app.get("/v1/sync")
def sync_endpoint() -> dict[str, str]:
    return {"runs_on": threading.current_thread().name}


@app.get("/v1/async")
async def async_endpoint() -> dict[str, str]:
    return {"runs_on": threading.current_thread().name}


@app.get("/v1/pool")
async def pool() -> dict[str, float]:
    limiter = anyio.to_thread.current_default_thread_limiter()
    return {"total_tokens": limiter.total_tokens}


c = TestClient(app)
print("def endpoint runs on:  ", c.get("/v1/sync").json()["runs_on"])
print("async endpoint runs on:", c.get("/v1/async").json()["runs_on"])
print("default threadpool budget (whole process, ALL def endpoints):",
      c.get("/v1/pool").json()["total_tokens"])
print("\n=> 40 threads ÷ 3s-per-call ≈ 13 req/s before EVERY def endpoint stalls (03.6)")
