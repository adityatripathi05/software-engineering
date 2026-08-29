"""Lab for 02.1 Resource modelling and URI design.

Reproduces the incident's two mechanisms: FastAPI's default trailing-slash 307
whose Location is built from the URL *the app sees* (behind a proxy, an internal
host), and the client half — httpx, like every careful HTTP client, DROPS the
Authorization header when a redirect changes host. Redirect + wrong host = 401.
"""
import httpx
from fastapi import FastAPI, Request

app = FastAPI()          # redirect_slashes=True is the default


@app.get("/v1/invoices")
async def list_invoices(request: Request) -> dict[str, str | None]:
    return {"authorization_seen": request.headers.get("authorization")}


@app.get("/internal-redirect")
async def internal_redirect(request: Request):
    # stands in for the 307 a proxy-blind app builds: same app, "different" host
    from fastapi.responses import RedirectResponse
    return RedirectResponse("http://api-internal:8000/v1/invoices", status_code=307)


async def main() -> None:
    transport = httpx.ASGITransport(app=app)     # every host resolves to this app
    async with httpx.AsyncClient(transport=transport, follow_redirects=True,
                                 base_url="http://api.ledgerly.com") as c:
        r = await c.get("/v1/invoices/", headers={"Authorization": "Bearer key_live_7ac"})
        print("GET /v1/invoices/ (trailing slash), same-host 307:")
        print(f"  final URL {r.url}  auth arrived: {r.json()['authorization_seen']!r}\n")

        r = await c.get("/internal-redirect", headers={"Authorization": "Bearer key_live_7ac"})
        print("307 whose Location names ANOTHER host (the proxy-blind app's view):")
        print(f"  final URL {r.url}  auth arrived: {r.json()['authorization_seen']!r}")
        print("\n=> the client followed the redirect and, on the host change, STRIPPED")
        print("   Authorization — correct client hygiene, surfacing as intermittent 401s.")
        print("   A redirect is a second request whose target your app computes (02.1);")
        print("   rule: one canonical URI form, no slash redirects.")


import asyncio
asyncio.run(main())
