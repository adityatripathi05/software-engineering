"""Lab for 01.4 Content negotiation and HTTP caching.

Reproduces the incident's decision rule with a minimal shared cache standing in
for the CDN: `Cache-Control: max-age=60` WITHOUT `private` marks a response
storable by ANY cache — so an authenticated invoice list is served to the next
tenant. With `private`, the shared cache refuses. The cache here implements
only the real rule that failed.
"""
from fastapi import FastAPI, Header, Response
from fastapi.testclient import TestClient

app = FastAPI()

TENANT_DATA = {"key_tenant_A": ["inv_A1 4,200.00"], "key_tenant_B": ["inv_B1 9.99"]}


@app.get("/v1/invoices-leaky")
async def leaky(response: Response, authorization: str = Header()) -> list[str]:
    response.headers["Cache-Control"] = "max-age=60"          # ⚠️ no `private`
    return TENANT_DATA[authorization]


@app.get("/v1/invoices-safe")
async def safe(response: Response, authorization: str = Header()) -> list[str]:
    response.headers["Cache-Control"] = "private, max-age=60"
    return TENANT_DATA[authorization]


class MiniSharedCache:
    """A CDN's storability rule, and nothing else: shared caches may store any
    response that says it is cacheable — unless it says `private`."""

    def __init__(self, client: TestClient):
        self.client, self.store = client, {}

    def get(self, url: str, token: str) -> tuple[str, list[str]]:
        if url in self.store:
            return "HIT (shared cache)", self.store[url]
        r = self.client.get(url, headers={"Authorization": token})
        cc = r.headers.get("cache-control", "")
        if "max-age" in cc and "private" not in cc and "no-store" not in cc:
            self.store[url] = r.json()                        # keyed by URL alone
        return f"MISS (origin; Cache-Control: {cc})", r.json()


cache = MiniSharedCache(TestClient(app))

print("-- Tuesday 16:10: the CDN goes in front of api.ledgerly.com --")
for token in ("key_tenant_A", "key_tenant_B"):
    how, body = cache.get("/v1/invoices-leaky", token)
    print(f"  {token} -> {how}: {body}")
print("=> tenant B received tenant A's invoices: the cache key is the URL, and")
print("   nothing told the shared cache this response was per-credential (01.4)\n")

for token in ("key_tenant_A", "key_tenant_B"):
    how, body = cache.get("/v1/invoices-safe", token)
    print(f"  {token} -> {how}: {body}")
print("=> `private` forbids shared storage; every authenticated response carries")
print("   it (or no-store) as a CI-checked invariant (01.4).")
