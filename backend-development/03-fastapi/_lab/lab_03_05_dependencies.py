"""Lab for 03.5 Dependency injection.

Reproduces the teardown-timing capture: code after a dependency's `yield` runs
AFTER the handler has produced the response — so a commit placed there races a
success the client may already hold. The events list is the proof.
"""
from typing import Annotated, AsyncIterator

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

events: list[str] = []


async def get_session() -> AsyncIterator[str]:
    events.append("dependency: setup (session opened)")
    yield "session"
    events.append("dependency: teardown AFTER yield (this is where the commit was)")


app = FastAPI()


@app.post("/v1/invoices")
async def create_invoice(session: Annotated[str, Depends(get_session)]) -> dict[str, str]:
    events.append("handler: ran, returning the 201 payload")
    return {"id": "inv_9f2c41"}


c = TestClient(app)
r = c.post("/v1/invoices")
print(f"client got HTTP {r.status_code}: {r.json()}")
print("\nexecution order:")
for e in events:
    print(" ", e)
print("\n=> teardown runs after the handler produced the response; over a real")
print("   transport the body has LEFT by then — a failed commit there contradicts")
print("   a success the customer already recorded (03.5's incident).")
