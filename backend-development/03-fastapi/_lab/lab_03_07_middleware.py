"""Lab for 03.7 Middleware.

Reproduces both core captures: the LAST add_middleware call wraps OUTERMOST
(enter/exit order recorded through two BaseHTTPMiddleware), and an exception
raised INSIDE middleware bypasses the type-specific exception handlers — the
mechanism behind the preflight incident.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from starlette.middleware.base import BaseHTTPMiddleware

events: list[str] = []


class Recorder(BaseHTTPMiddleware):
    def __init__(self, app, name: str):
        super().__init__(app)
        self.name = name

    async def dispatch(self, request, call_next):
        events.append(f"{self.name}-enter")
        response = await call_next(request)
        events.append(f"{self.name}-exit")
        return response


class AuditError(Exception):
    pass


class RaisingAudit(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.headers.get("x-poison"):
            raise AuditError("unguarded parse, as in the preflight incident")
        return await call_next(request)


app = FastAPI()
app.add_middleware(Recorder, name="FIRST-ADDED")
app.add_middleware(Recorder, name="LAST-ADDED")
app.add_middleware(RaisingAudit)                     # added last → OUTERMOST of the three


@app.exception_handler(AuditError)
async def audit_handler(request: Request, exc: AuditError) -> JSONResponse:
    return JSONResponse({"handled": "by typed handler"}, status_code=400)


@app.get("/v1/ping")
async def ping() -> dict[str, bool]:
    events.append("handler")
    return {"ok": True}


c = TestClient(app, raise_server_exceptions=False)

c.get("/v1/ping")
print("wrapping order:", " -> ".join(events))
print("=> last added is outermost (the review comment 'added last so nothing")
print("   escapes it' put the audit middleware ABOVE CORS)\n")

r = c.get("/v1/ping", headers={"x-poison": "1"})
print(f"AuditError raised in MIDDLEWARE  -> HTTP {r.status_code} (typed handler NOT used)")


@app.get("/v1/handler-raise")
async def handler_raise() -> None:
    raise AuditError("same exception, raised in a handler")


r = c.get("/v1/handler-raise")
print(f"same AuditError raised in HANDLER -> HTTP {r.status_code} {r.json()}")
print("\n=> handlers live inside ExceptionMiddleware; anything raised above it is a bare 500")
