"""Lab for 03.8 Exception handling and error mapping.

Reproduces: one handler registered on *Starlette's* HTTPException catches
FastAPI's too (they are the same class hierarchy — the 03.8 registration rule);
RequestValidationError overridden to a problem body (so the wire matches the
02.9 catalogue, not the auto-documented shape); and TaskGroup wrapping failures
in ExceptionGroup — the `except*` caveat.
"""
import asyncio

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()


@app.exception_handler(StarletteHTTPException)
async def problem_http(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        {"type": "https://api.ledgerly.com/problems/generic", "title": exc.detail,
         "status": exc.status_code},
        status_code=exc.status_code, media_type="application/problem+json",
    )


@app.exception_handler(RequestValidationError)
async def problem_validation(request: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        {"type": "https://api.ledgerly.com/problems/validation", "title": "Validation problem",
         "status": 422, "errors": [e["loc"] for e in exc.errors()]},
        status_code=422, media_type="application/problem+json",
    )


class Body(BaseModel):
    amount: int


@app.post("/v1/adjust")
async def adjust(b: Body) -> dict[str, bool]:
    return {"ok": True}


@app.get("/v1/missing")
async def missing() -> None:
    raise HTTPException(status_code=404, detail="No such invoice in this tenant")


c = TestClient(app)

r = c.get("/v1/missing")
print(f"FastAPI HTTPException via handler registered on STARLETTE's class:")
print(f"  HTTP {r.status_code} {r.headers['content-type']}")
print(f"  {r.json()}\n")

r = c.post("/v1/adjust", json={"amount": "not-a-number"})
print(f"overridden RequestValidationError -> HTTP {r.status_code} {r.headers['content-type']}")
print(f"  {r.json()}")
print("=> the wire now matches the catalogue — but the OpenAPI document still")
print("   advertises HTTPValidationError unless 422 is declared (03.13)\n")


async def taskgroup_wrapping() -> None:
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(asyncio.sleep(0.01))
            async def boom() -> None:
                raise ValueError("worker failed")
            tg.create_task(boom())
    except* ValueError as eg:
        print("TaskGroup failure arrives as:", type(eg).__name__,
              "wrapping", [type(e).__name__ for e in eg.exceptions])
        print("=> a plain `except ValueError:` would MISS this (03.8's caveat)")


asyncio.run(taskgroup_wrapping())
