"""Lab for 03.1 Application structure and ASGI.

Reproduces the notebook's core captures: add_middleware wrapping order (the LAST
middleware added is the OUTERMOST — verified by recording enter/exit order), and
the route table an app assembles (what app.openapi() and routing both read).
"""
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

events: list[str] = []


def make_asgi_middleware(name: str):
    class Recorder:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            if scope["type"] != "http":
                return await self.app(scope, receive, send)
            events.append(f"{name}-enter")
            await self.app(scope, receive, send)
            events.append(f"{name}-exit")

    return Recorder


app = FastAPI()
app.add_middleware(make_asgi_middleware("FIRST-ADDED"))
app.add_middleware(make_asgi_middleware("LAST-ADDED"))


@app.get("/v1/ping")
async def ping() -> dict[str, bool]:
    events.append("handler")
    return {"ok": True}


client = TestClient(app)
client.get("/v1/ping")
print("call order:", " -> ".join(events))
print("=> the LAST middleware added is the OUTERMOST (03.1/03.7 canon)")

print("\nroute table (what routing and openapi() both read):")
for r in app.routes:
    if isinstance(r, APIRoute):
        print(f"  {sorted(r.methods)} {r.path}  name={r.name!r}")
