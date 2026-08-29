## Module recap

**Running system:** Ledgerly, a B2B SaaS invoicing API (`api.ledgerly.com`) with a browser dashboard
(`app.ledgerly.com`), PDF invoice rendering, and customer integrations that call the API from their
own servers. Modules 02–04 continue with the same product.

**What this module built up.** A request is ten steps, not one: DNS, TCP, TLS, framing, accept,
parse, ASGI, routing, handler, write. Each notebook takes one of those steps and asks what it costs
and how it fails. By the end you can describe any HTTP interaction in terms of *who parses what*,
*who may replay it*, *who may store it*, and *who may read it*.

**The incidents, and what each one taught.**

| # | Incident | The general lesson |
|---|---|---|
| 01.1 | A blocking PDF render fills the kernel accept queue; the app histogram reports 11 ms while customers wait 5 s | Measure latency at two points; app metrics cannot see queueing |
| 01.2 | `GET /invoices/{id}/send` is fetched 14,000 times by link scanners, emailing real customers | Method semantics are a promise to infrastructure you will never meet |
| 01.3 | A `429` loses its `Retry-After` header; one client's retry loop becomes 8,400 req/s | Status codes are branch instructions for the caller's retry logic |
| 01.4 | A new CDN caches a non-`private` invoice list and serves one tenant's data to another | `Vary` is the cache key; `private` is the default for authenticated responses |
| 01.5 | A browser tightens the `SameSite=Lax` default; SSO users enter a redirect loop | The enforcement point for cookies is software you do not deploy |
| 01.6 | Autoscaling 1 → 6 replicas turns an in-memory idempotency guard into duplicate invoices | Stateless means *any replica can serve any request* |
| 01.7 | uvicorn's 5 s keep-alive under a 60 s load balancer produces 0.2% phantom `502`s for eleven days | Upstream must hold connections longer than downstream reuses them |
| 01.8 | `cert.pem` instead of `fullchain.pem`: browsers fine, every machine client broken | Never validate TLS with a browser |
| 01.9 | `allow_origin_regex=".*"` with credentials lets any website read logged-in users' data | CORS is a *relaxation* of the Same-Origin Policy, not a protection |
| 01.10 | `--forwarded-allow-ips="*"` lets an attacker spoof their IP; 2.1 M login attempts, 3 rejections | Trust is a property of the connection, not the header |

**The pattern across all ten.** Six of these incidents produced **no errors and no alerts**, and in
most of the others the alert that fired pointed at the wrong layer (a proxy SLO, a flapping `5xx`
threshold, a fraud rule). The
service reported itself healthy while leaking data, duplicating records, or being evaded. The
recurring diagnostic move is comparing two vantage points — edge vs origin, LB count vs app count,
browser vs clean trust store, one replica vs many — and treating the *discrepancy* as the signal.
That habit is worth more than any single fact in this module.

**Config invariants established here** (all asserted by CI tests in the notebooks):

```text
client keep-alive  <  proxy idle timeout  <  server keep-alive     (01.7)
--forwarded-allow-ips = <private CIDR>, never "*"                  (01.10)
ssl_certificate = fullchain.pem, never cert.pem                    (01.8)
authenticated responses: Cache-Control private|no-store            (01.4)
CORS: explicit origin list; no regex, no reflection                (01.9)
no state-changing GET/HEAD routes                                  (01.2)
429/503 carry Retry-After; 401 carries WWW-Authenticate;
  405 carries Allow; 201 carries Location                          (01.3)
```

**What module 02 assumes.** That you can choose a method and status without hesitating, that you
know why idempotency keys exist before you implement them, that `ETag`/`If-Match` is available as a
concurrency tool, and that you treat every response header as part of the API contract.
