"""Lab for 03.3 Request/response models.

Reproduces: response_model as a serialisation FILTER (undeclared ORM fields never
leave), ResponseValidationError when a handler violates its own declared contract
(FastAPI answers 500 rather than shipping a malformed body), and extra="forbid"
rejecting unknown input fields.
"""
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict

app = FastAPI()


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    country: str


ORM_ROW = SimpleNamespace(
    id="cus_8f21ac", name="Nordwind Logistik GmbH", country="DE",
    internal_risk_score=0.87, crm_notes="difficult renewal call",   # must never leave
)


@app.get("/v1/customers/{cid}", response_model=CustomerOut)
async def get_customer(cid: str) -> CustomerOut:
    return ORM_ROW  # 9-ish fields in, declared 3 out


@app.get("/v1/broken", response_model=CustomerOut)
async def broken() -> CustomerOut:
    return SimpleNamespace(id="cus_1")  # violates the declared contract


class InvoiceCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    customer_id: str


@app.post("/v1/invoices")
async def create(body: InvoiceCreate) -> dict[str, str]:
    return {"ok": body.customer_id}


c = TestClient(app, raise_server_exceptions=False)

print("response_model filters:", c.get("/v1/customers/cus_8f21ac").json())
print("=> internal_risk_score / crm_notes never serialised\n")

r = c.get("/v1/broken")
print(f"handler violating its own contract -> HTTP {r.status_code}")
print("=> ResponseValidationError: FastAPI protects the contract in BOTH directions\n")

r = c.post("/v1/invoices", json={"customer_id": "cus_1", "surprise": 1})
print(f"extra='forbid' vs unknown input field -> HTTP {r.status_code}:",
      r.json()["detail"][0]["type"])
