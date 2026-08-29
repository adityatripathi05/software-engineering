"""Lab for 03.9 Lifespan and application lifecycle.

Reproduces: lifespan as one context manager around the serving lifetime (the
`with TestClient(...)` block sends startup/shutdown; a bare TestClient sends
NEITHER — the fixture trap), yielded state becoming request.state, and a
supervised background task whose restarts are counted — with the load-bearing
re-raise on cancellation.
"""
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

events: list[str] = []
RESTARTS = {"count": 0}


async def sampler() -> None:
    """Supervised loop: restarts counted; cancellation re-raised, never swallowed."""
    while True:
        try:
            await asyncio.sleep(3600)
        except asyncio.CancelledError:
            events.append("sampler: cancelled at shutdown — re-raising")
            raise                      # swallow this and shutdown hangs (03.9)
        except Exception:
            RESTARTS["count"] += 1


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[dict]:
    events.append("lifespan: startup (create engine/clients HERE, post-fork)")
    task = asyncio.create_task(sampler())
    try:
        yield {"engine": "ENGINE-OBJECT", "sampler": task}
    finally:
        events.append("lifespan: shutdown (finally — teardown mirrors startup)")
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(lifespan=lifespan)


@app.get("/v1/state")
async def state(request: Request) -> dict[str, str]:
    return {"engine_from_request_state": request.state.engine}


print("-- bare TestClient (the fixture trap): no lifespan events --")
bare = TestClient(app)
print("events so far:", events or "(none — startup never ran)")

print("\n-- with-block: full lifecycle --")
with TestClient(app) as c:
    print("request sees yielded state:", c.get("/v1/state").json())
print("events:")
for e in events:
    print(" ", e)
print("\n=> traffic exists only between startup.complete and lifespan.shutdown;")
print("   a fixture that skips the with-block tests a process state that")
print("   cannot exist in production (03.9).")
