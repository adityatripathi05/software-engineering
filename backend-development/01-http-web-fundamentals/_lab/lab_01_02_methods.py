"""Lab for 01.2 Methods, safety, idempotency.

Reproduces the incident's mechanism: a state-changing GET is executed by every
fetch — link previewers carry no intent, only the method's promise. Then the
semantics table (PUT idempotent, POST not) and the route-table guard that closes
the incident.
"""
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

EMAILS_SENT: list[str] = []
INVOICES: dict[str, dict] = {}

app = FastAPI()


@app.get("/v1/invoices/{invoice_id}/send")        # ⚠️ the one-click chat link
def send_invoice_by_link(invoice_id: str) -> dict[str, int]:
    EMAILS_SENT.append(invoice_id)
    return {"emails_sent_total": len(EMAILS_SENT)}


@app.put("/v1/invoices/{invoice_id}")
def put_invoice(invoice_id: str, body: dict) -> dict:
    INVOICES[invoice_id] = body                    # full replace: repeat = same state
    return INVOICES[invoice_id]


@app.post("/v1/invoices")
def post_invoice(body: dict) -> dict[str, int]:
    INVOICES[f"inv_{len(INVOICES)}"] = body        # repeat = ANOTHER invoice
    return {"invoice_count": len(INVOICES)}


c = TestClient(app)

print("-- a 'resend' link implemented as GET, fetched by scanners --")
for fetcher in ("Teams preview bot", "Outlook SafeLinks", "a colleague's browser prefetch"):
    r = c.get("/v1/invoices/inv_9f2c41/send")
    print(f"  {fetcher:32} -> emails_sent_total={r.json()['emails_sent_total']}")
print("=> nobody 'clicked'; the method promised safety and the handler lied (01.2)\n")

print("-- idempotency: repeat the request, compare the state --")
c.put("/v1/invoices/inv_1", json={"total": "100.00"})
c.put("/v1/invoices/inv_1", json={"total": "100.00"})
print(f"  PUT twice  -> {len([k for k in INVOICES if k == 'inv_1'])} invoice (same state)")
c.post("/v1/invoices", json={"total": "50.00"})
c.post("/v1/invoices", json={"total": "50.00"})
print(f"  POST twice -> invoice_count={len(INVOICES)} (a retry without an idempotency key duplicates)\n")

print("-- the CI guard that closes the incident --")
MUTATING_NAMES = {"send_invoice_by_link"}          # in real life: naming/marker convention
for route in app.routes:
    if isinstance(route, APIRoute) and route.methods & {"GET", "HEAD"}:
        if route.endpoint.__name__ in MUTATING_NAMES:
            print(f"  FAIL: {sorted(route.methods)} {route.path} is state-changing "
                  "on a safe method")
