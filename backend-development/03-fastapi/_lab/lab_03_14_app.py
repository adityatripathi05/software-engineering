"""Lab app for 03.14 Production deployment.

The minimal Ledgerly-shaped app the signals lab (lab_03_14_signals.py) drives:
a lifespan that prints its pid (proving per-worker startup/shutdown), a 4-second
route for drain experiments, and a 30-second route for graceful-timeout expiry.
"""
import asyncio
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[lifespan] startup in pid={os.getpid()}", flush=True)
    yield
    print(f"[lifespan] shutdown in pid={os.getpid()}", flush=True)


app = FastAPI(lifespan=lifespan)


@app.get("/v1/ping")
async def ping() -> dict[str, int]:
    return {"pid": os.getpid()}


@app.get("/v1/slow")
async def slow() -> dict[str, str]:
    await asyncio.sleep(4)
    return {"status": "rendered", "invoice": "inv_9f2c41"}


@app.get("/v1/very-slow")
async def very_slow() -> dict[str, str]:
    await asyncio.sleep(30)
    return {"status": "rendered"}
