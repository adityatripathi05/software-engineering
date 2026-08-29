"""Lab for 02.4 Contract-first design and OpenAPI.

Reproduces the leak: with NO declared response type, FastAPI serialises the
whole returned object — internal fields included, documented nowhere. With
`response_model`, the declared field list is both the filter and the published
contract. Then the artefact rule: the generated document diffed against a
committed snapshot turns any contract change into a visible failure.
"""
import json
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict

ORM_ROW = SimpleNamespace(
    id="cus_8f21ac", name="Nordwind Logistik GmbH", email="ap@nordwind.example",
    country="DE", created_at="2024-11-02",
    internal_risk_score=0.87, acquisition_channel="outbound",
    crm_notes="difficult renewal call", stripe_customer_id="cus_stripe_991",
)


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    email: str
    country: str
    created_at: str


app = FastAPI()


@app.get("/v1/customers-undeclared/{cid}")
async def undeclared(cid: str):                       # ⚠️ no response type at all
    return ORM_ROW


@app.get("/v1/customers/{cid}", response_model=CustomerOut)
async def declared(cid: str) -> CustomerOut:
    return ORM_ROW


c = TestClient(app)

print("no declared response type — what actually left the building:")
print(" ", json.dumps(c.get("/v1/customers-undeclared/cus_8f21ac").json()))
print("\nresponse_model=CustomerOut — the declared five:")
print(" ", json.dumps(c.get("/v1/customers/cus_8f21ac").json()))

spec = app.openapi()
resp = spec["paths"]["/v1/customers-undeclared/{cid}"]["get"]["responses"]["200"]
print("\n...and the undeclared route's documented 200 schema:",
      resp["content"]["application/json"]["schema"])
print("=> nine fields served, ZERO documented — for seven months (02.4)\n")

committed_snapshot = json.dumps(spec, sort_keys=True)          # 'openapi.json' in git
# simulate a PR that narrows the contract:
spec["components"]["schemas"]["CustomerOut"]["properties"].pop("email")
current = json.dumps(app.openapi(), sort_keys=True)
print("CI freshness/diff gate:", "PASS (no contract change)"
      if committed_snapshot == current else
      "FAIL — the contract changed; the diff must appear in the PR that caused it")
