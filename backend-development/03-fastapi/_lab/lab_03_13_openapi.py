"""Lab for 03.13 OpenAPI customisation.

Reproduces every captured transcript in the notebook: default operationIds, the
openapi() cache, declared responses (and the auto-422), components naming, docs
gating (docs_url=None vs openapi_url=None), the -Input/-Output schema split and
its opt-out flag, the duplicate-name guard, the 422 override, and router-level
responses merging.

Run:  python lab_03_13_openapi.py            (pinned stack; no infra needed)
"""
import json
from decimal import Decimal
from typing import Literal

from fastapi import FastAPI, APIRouter
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

import fastapi, pydantic, starlette
print(f"fastapi={fastapi.__version__} pydantic={pydantic.VERSION} starlette={starlette.__version__}")
print("=" * 70)


class ProblemDetails(BaseModel):
    type: str
    title: str
    status: int
    detail: str | None = None


class InvoiceOut(BaseModel):
    id: str = Field(examples=["inv_9f2c41"])
    total: Decimal
    status: Literal["draft", "sent", "paid", "void"]


class InvoiceCreate(BaseModel):
    customer_id: str
    currency: str = "EUR"


router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get(
    "/{invoice_id}",
    response_model=InvoiceOut,
    name="getInvoice",
    summary="Retrieve an invoice",
    responses={
        404: {"model": ProblemDetails, "description": "No such invoice in this tenant"},
        429: {"model": ProblemDetails, "description": "Rate limit exceeded"},
    },
)
async def get_invoice(invoice_id: str) -> InvoiceOut:
    raise NotImplementedError


@router.post("", response_model=InvoiceOut, status_code=201)
async def create_invoice(body: InvoiceCreate) -> InvoiceOut:
    """No explicit name= — what operationId does FastAPI generate?"""
    raise NotImplementedError


@router.get("/{invoice_id}/pdf", name="getInvoicePdf", deprecated=True)
async def get_invoice_pdf(invoice_id: str) -> None:
    raise NotImplementedError


internal = APIRouter(prefix="/internal", tags=["internal"])


@internal.get("/cache-stats", include_in_schema=False, name="cacheStats")
async def cache_stats() -> dict[str, int]:
    return {}


app = FastAPI(
    title="Ledgerly Invoicing API",
    version="2.0.0",
    openapi_tags=[
        {"name": "invoices", "description": "Create, send and download invoices."},
    ],
)
app.include_router(router, prefix="/v1")
app.include_router(internal, prefix="/v1")

# --- 1. default operationIds before any customisation
print("\n--- 1. operationIds as FastAPI generates them (no name=) ---")
spec = app.openapi()
for path, ops in spec["paths"].items():
    for method, op in ops.items():
        print(f"{method.upper():6} {path:30} operationId={op['operationId']}")

# --- 2. is include_in_schema route absent?
print("\n--- 2. /v1/internal/cache-stats in paths?", "/v1/internal/cache-stats" in spec["paths"])

# --- 3. the cache: mutate the route table AFTER first openapi() call
print("\n--- 3. openapi() cache behaviour ---")
def use_stable_operation_ids(a: FastAPI) -> None:
    seen: set[str] = set()
    for route in a.routes:
        if isinstance(route, APIRoute):
            if route.name in seen:
                raise RuntimeError(f"Duplicate operationId {route.name!r}")
            seen.add(route.name)
            route.operation_id = route.name

use_stable_operation_ids(app)
spec2 = app.openapi()
print("after use_stable_operation_ids, spec is same object as before:", spec2 is spec)
print("getInvoice id in cached spec:", spec2["paths"]["/v1/invoices/{invoice_id}"]["get"]["operationId"])
app.openapi_schema = None  # bust the cache
spec3 = app.openapi()
print("after cache bust:")
for path, ops in spec3["paths"].items():
    for method, op in ops.items():
        print(f"{method.upper():6} {path:30} operationId={op['operationId']}")

# --- 4. what the responses={} declaration produced (note the auto-422!)
print("\n--- 4. declared responses for GET /v1/invoices/{invoice_id} ---")
print(json.dumps(spec3["paths"]["/v1/invoices/{invoice_id}"]["get"]["responses"], indent=2))

# --- 5. components/schemas names
print("\n--- 5. components/schemas keys ---")
print(sorted(spec3["components"]["schemas"].keys()))

# --- 6. deprecated flag
print("\n--- 6. deprecated on pdf route:", spec3["paths"]["/v1/invoices/{invoice_id}/pdf"]["get"].get("deprecated"))

# --- 7. tags metadata
print("\n--- 7. top-level tags:", json.dumps(spec3.get("tags")))

# --- 8. docs gating: docs_url=None leaves /openapi.json exposed
print("\n--- 8. docs gating ---")
app_prod = FastAPI(docs_url=None, redoc_url=None)
@app_prod.get("/v1/ping")
async def ping() -> dict[str, bool]:
    return {"ok": True}
c = TestClient(app_prod)
for u in ("/docs", "/redoc", "/openapi.json"):
    print(f"docs_url=None:              GET {u:14} -> {c.get(u).status_code}")

app_dark = FastAPI(openapi_url=None)
@app_dark.get("/v1/ping")
async def ping2() -> dict[str, bool]:
    return {"ok": True}
c2 = TestClient(app_dark)
for u in ("/docs", "/redoc", "/openapi.json"):
    print(f"openapi_url=None:           GET {u:14} -> {c2.get(u).status_code}")

# --- 9. separate input/output schemas: model with defaults in both directions
print("\n--- 9. -Input/-Output split ---")
app_io = FastAPI()
class Adjustment(BaseModel):
    amount: Decimal
    reason: str = "manual"
@app_io.post("/adjust", response_model=Adjustment)
async def adjust(a: Adjustment) -> Adjustment:
    return a
print(sorted(app_io.openapi()["components"]["schemas"].keys()))

# --- 10. ...and the opt-out flag (Version note)
app_flag = FastAPI(separate_input_output_schemas=False)
@app_flag.post("/adjust", response_model=Adjustment)
async def adjust_single(a: Adjustment) -> Adjustment:
    return a
print("separate_input_output_schemas=False:",
      sorted(app_flag.openapi()["components"]["schemas"].keys()))

# --- 11. duplicate name check fires
print("\n--- 11. duplicate name check ---")
app_dup = FastAPI()
r_dup = APIRouter()
@r_dup.get("/a", name="listInvoices")
async def dup_a() -> None: ...
@r_dup.get("/b", name="listInvoices")
async def dup_b() -> None: ...
app_dup.include_router(r_dup)
try:
    use_stable_operation_ids(app_dup)
except RuntimeError as e:
    print("RuntimeError:", e)

# --- 12. declaring 422 replaces the auto-doc; router-level responses merge
print("\n--- 12. 422 override + router-level responses merge ---")
class AdjBody(BaseModel):
    amount: int

app_merge = FastAPI()
r_m = APIRouter()

@r_m.post("/one", responses={422: {"model": ProblemDetails, "description": "Validation problem"}})
async def one(b: AdjBody) -> dict[str, bool]:
    return {"ok": True}

@r_m.post("/two")
async def two(b: AdjBody) -> dict[str, bool]:
    return {"ok": True}

app_merge.include_router(
    r_m, prefix="/v1",
    responses={429: {"model": ProblemDetails, "description": "Rate limit exceeded"}},
)
m_spec = app_merge.openapi()
for p in ("/v1/one", "/v1/two"):
    resp = m_spec["paths"][p]["post"]["responses"]
    summary = {code: r["content"]["application/json"]["schema"].get("$ref", "?")
               for code, r in resp.items() if "content" in r}
    print(p, "->", json.dumps(summary))
