"""Lab for 01.5 Cookies and sessions.

Reproduces what an HTTP library CAN show: the Set-Cookie contract the server
writes (attributes are the whole security model) and the jar sending it back.
⚠️ The incident's mechanism — Chrome rejecting a `SameSite=Lax` cookie set in
response to a cross-site POST — is enforced INSIDE the browser: no HTTP client
reproduces it, which is exactly the notebook's point (the enforcement point for
cookies is software you do not deploy). This lab pins the server's half.
"""
from fastapi import FastAPI, Response
from fastapi.testclient import TestClient

app = FastAPI()


@app.post("/sso/acs")
async def acs(response: Response) -> dict[str, str]:
    # what the IdP's cross-site form POST lands on
    response.set_cookie(
        "ledgerly_session", "sess_7f3a",
        httponly=True, secure=True, samesite="lax", max_age=3600, path="/",
    )
    return {"login": "ok"}


@app.get("/v1/me")
async def me(request_cookie: str | None = None) -> dict[str, str | None]:
    return {"session_seen": request_cookie}


c = TestClient(app, base_url="https://app.ledgerly.com")

r = c.post("/sso/acs")
print("Set-Cookie written by /sso/acs:")
print(" ", r.headers["set-cookie"])
print("\nattribute meanings (each one is a promise the BROWSER enforces):")
for attr, meaning in [
    ("HttpOnly", "JS cannot read it (XSS containment)"),
    ("Secure", "never sent over plain HTTP"),
    ("SameSite=Lax", "not attached to cross-site subrequests/POSTs — and ⚠️ not "
                     "ACCEPTED from a cross-site POST response by modern Chrome: "
                     "the 01.5 incident, browser-enforced, invisible to this client"),
    ("Max-Age/Path", "lifetime and scope"),
]:
    print(f"  {attr:14} {meaning}")

r = c.get("/v1/me")
print("\nnext request from the same client jar carries:",
      dict(c.cookies).get("ledgerly_session"))
print("\n=> the server writes attributes; the browser decides. A browser rollout can")
print("   change your login flow with zero deploys on your side (01.5). SameSite")
print("   enforcement itself needs a real browser — see the notebook's incident.")
