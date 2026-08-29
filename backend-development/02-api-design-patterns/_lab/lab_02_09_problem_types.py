"""Lab for 02.9 Error responses (RFC 9457).

Reproduces the incident's mechanism: a client that branches on the human prose
in `detail` breaks the day a copy edit ships; a client branching on the stable
`type` URI does not notice. The problem body is served by a real endpoint.
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

WORDING = {"v": "This idempotency key was already used."}       # before the edit

app = FastAPI()


@app.post("/v1/invoices")
async def create() -> JSONResponse:
    return JSONResponse(
        {"type": "https://api.ledgerly.com/problems/idempotency-key-reused",
         "title": "Idempotency key reused", "status": 422, "detail": WORDING["v"]},
        status_code=422, media_type="application/problem+json")


c = TestClient(app)


def client_parsing_detail(body: dict) -> str:
    """The customer's overnight sync: string-matching the prose."""
    if "already used" in body["detail"]:
        return "fetch existing invoice and continue"
    return "UNKNOWN ERROR — halt the batch"


def client_branching_on_type(body: dict) -> str:
    match body["type"].rsplit("/", 1)[-1]:
        case "idempotency-key-reused":
            return "fetch existing invoice and continue"
        case _:
            return "unhandled problem type — halt"


body = c.post("/v1/invoices").json()
print("before the copy edit:", body["detail"])
print("  detail-parser :", client_parsing_detail(body))
print("  type-brancher :", client_branching_on_type(body))

WORDING["v"] = "An invoice with this idempotency key exists; fetch it instead."
body = c.post("/v1/invoices").json()
print("\nafter a harmless copy edit:", body["detail"])
print("  detail-parser :", client_parsing_detail(body))
print("  type-brancher :", client_branching_on_type(body))

print("\n=> 4,100 invoices halted on a wording change. `type` is the contract;")
print("   `detail` is documented as mutable prose (02.9). If clients parse detail,")
print("   it is because you never gave them a stable type.")
