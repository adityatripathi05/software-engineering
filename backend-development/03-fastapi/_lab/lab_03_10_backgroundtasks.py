"""Lab for 03.10 BackgroundTasks vs real workers.

Reproduces the delivery-contract captures: the task runs AFTER the response is
produced; a crashing task cannot change the 200 the client already holds; and
nothing records that a task existed — at-most-once, in-process, unrecorded.
"""
from fastapi import BackgroundTasks, FastAPI
from fastapi.testclient import TestClient

events: list[str] = []
app = FastAPI()


def emit_usage_event(invoice_id: str) -> None:
    events.append(f"background: usage event for {invoice_id} emitted (AFTER response)")


def crashing_task(invoice_id: str) -> None:
    events.append("background: about to crash")
    raise RuntimeError("metering blip — and the event is simply GONE")


@app.post("/v1/invoices")
async def create(tasks: BackgroundTasks) -> dict[str, str]:
    tasks.add_task(emit_usage_event, "inv_9f2c41")
    events.append("handler: returning 201")
    return {"id": "inv_9f2c41"}


@app.post("/v1/invoices-crashing")
async def create_crashing(tasks: BackgroundTasks) -> dict[str, str]:
    tasks.add_task(crashing_task, "inv_9f2c41")
    return {"id": "inv_9f2c41"}


c = TestClient(app, raise_server_exceptions=False)

r = c.post("/v1/invoices")
print(f"client got HTTP {r.status_code}; order was:")
for e in events:
    print(" ", e)

events.clear()
r = c.post("/v1/invoices-crashing")
print(f"\ncrashing task: client STILL got HTTP {r.status_code} — events: {events}")
print("=> the failure is invisible to the caller and unrecorded anywhere:")
print("   at-most-once, in-process, unrecorded (03.10). Must-happen side effects")
print("   ride the outbox row written in the business transaction instead.")
