"""Lab for 01.9 CORS.

Reproduces the bug-bounty finding: `allow_origin_regex=".*"` combined with
`allow_credentials=True` tells the browser that EVERY origin may read
authenticated responses — the pre-Same-Origin-Policy world, opt-in. The
explicit-list configuration answers the same preflight correctly.
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.cors import CORSMiddleware


def build(name: str, **cors) -> TestClient:
    app = FastAPI()
    app.add_middleware(CORSMiddleware, **cors)

    @app.get("/v1/invoices")
    async def invoices() -> list[str]:
        return ["inv_9f2c41 4,200.00"]        # authenticated data, in the incident

    return TestClient(app)


leaky = build("leaky", allow_origin_regex=".*", allow_credentials=True,
              allow_methods=["*"], allow_headers=["*"])
safe = build("safe", allow_origins=["https://app.ledgerly.com"], allow_credentials=True,
             allow_methods=["GET", "POST"], allow_headers=["Authorization"])

EVIL = "https://evil.example"
GOOD = "https://app.ledgerly.com"


def preflight(client: TestClient, origin: str) -> str:
    r = client.options("/v1/invoices", headers={
        "Origin": origin,
        "Access-Control-Request-Method": "GET",
    })
    aco = r.headers.get("access-control-allow-origin")
    acc = r.headers.get("access-control-allow-credentials")
    return f"HTTP {r.status_code}  allow-origin={aco!r}  allow-credentials={acc!r}"


print("-- allow_origin_regex='.*' + allow_credentials=True (the finding) --")
print(f"  preflight from {EVIL}: ", preflight(leaky, EVIL))
print("  => the browser is told: evil.example may send the user's cookies AND")
print("     read the response — CORS is a relaxation, and this relaxes everything\n")

print("-- explicit origin list --")
print(f"  preflight from {EVIL}: ", preflight(safe, EVIL))
print(f"  preflight from {GOOD}:", preflight(safe, GOOD))
print("\n=> no allow-origin header for evil.example means the browser withholds the")
print("   response. The invariant: explicit origin list; no regex, no reflection,")
print("   and credentials only ever with exact origins (01.9).")
