"""Lab for 03.14 Production deployment — root_path behind a prefix-stripping proxy.

Reproduces the notebook's capture: with FastAPI(root_path="/api"), handlers still
match the stripped path, request.scope["root_path"] carries the prefix, and the
OpenAPI document gains servers=[{"url": "/api"}] so /docs works through the proxy.

Run:  python lab_03_14_rootpath.py
"""
import json
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

app = FastAPI(root_path="/api")


@app.get("/v1/ping")
async def ping(request: Request) -> dict[str, str]:
    return {
        "root_path": request.scope["root_path"],
        "path": request.url.path,
        "docs_would_fetch": app.openapi_url or "",
    }


c = TestClient(app)
print("GET /v1/ping ->", json.dumps(c.get("/v1/ping").json()))
spec = c.get("/openapi.json").json()
print("openapi servers:", json.dumps(spec.get("servers")))
print("openapi has /v1/ping (not /api/v1/ping):", "/v1/ping" in spec["paths"])
