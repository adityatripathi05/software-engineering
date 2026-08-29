"""Lab for 03.2 Routing and parameters.

Reproduces the shadowing capture: /{invoice_id} registered BEFORE /summary makes
the literal route unreachable (first-wins matching) — while it still appears in
the OpenAPI document, because the document is generated from the route table,
not from reachability.
"""
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
router = APIRouter(prefix="/v1/invoices")


@router.get("/{invoice_id}", name="getInvoice")
async def get_invoice(invoice_id: str) -> dict[str, str]:
    return {"matched": "getInvoice", "invoice_id": invoice_id}


@router.get("/summary", name="getInvoiceSummary")   # registered AFTER the param route
async def get_summary() -> dict[str, str]:
    return {"matched": "getInvoiceSummary"}


app.include_router(router)
c = TestClient(app)

print("GET /v1/invoices/summary ->", c.get("/v1/invoices/summary").json())
print('=> the literal route is SHADOWED: "summary" was captured as invoice_id')
print("in OpenAPI paths anyway?:",
      "/v1/invoices/summary" in app.openapi()["paths"], " (the doc reads the table)")

app2 = FastAPI()
router2 = APIRouter(prefix="/v1/invoices")


@router2.get("/summary", name="getInvoiceSummary")  # literal BEFORE the param route
async def get_summary_fixed() -> dict[str, str]:
    return {"matched": "getInvoiceSummary"}


@router2.get("/{invoice_id}", name="getInvoice")
async def get_invoice_fixed(invoice_id: str) -> dict[str, str]:
    return {"matched": "getInvoice", "invoice_id": invoice_id}


app2.include_router(router2)
c2 = TestClient(app2)
print("\nfixed order: GET /v1/invoices/summary ->", c2.get("/v1/invoices/summary").json())
print("fixed order: GET /v1/invoices/inv_9f2c41 ->", c2.get("/v1/invoices/inv_9f2c41").json())
