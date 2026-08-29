# Module 01 — Self-Test

Retrieval practice for [HTTP & Web Fundamentals](README.md). Reading produces the *illusion*
of competence; answering is what builds the real thing. Attempt every question — aloud or on
paper — **before** opening the Answers section at the bottom. A wrong answer is the point:
it marks exactly where a re-read will pay.

**How to use these notes (applies to every module):**

- Before reading a notebook's *Mental Model*, state your own one-sentence version first.
- Answer each *Interview Question* aloud before reading its answer shape.
- Type and run at least one code block per notebook — never just read it.
- Reattempt this quiz about a week after finishing the module; the second attempt is the one
  that counts (spacing beats massing).

---

## Questions

1. A customer's retry loop hits you at 8,400 req/s. Your `429` responses are correct and
   documented. What single header went missing, and why did its absence turn polite retries
   into a flood?
2. Every browser works; every Python and Java integration fails the TLS handshake. What was
   misconfigured, and why do browsers mask the mistake?
3. Link scanners emailed real invoices 14,000 times without a single user clicking "send".
   Which HTTP promise was broken — and to whom is that promise actually made?
4. For eleven days, 0.2% of requests return phantom `502`s nobody can reproduce. Write, as an
   inequality, the timeout rule that prevents this entire class of failure.
5. A new CDN served tenant A's invoice list to tenant B. Name two response-header rules that
   would each, *alone*, have prevented it.
6. The app's latency histogram says 11 ms; customers wait 5 seconds. Where did the time go,
   and why can the app's own metrics never see it?
7. Why is CORS best described as a *relaxation* rather than a protection — and which exact
   configuration pair recreated the pre-Same-Origin-Policy world at Ledgerly?
8. Define "stateless" in the one sentence that would have prevented the duplicate-invoice
   incident. Where may per-request state legitimately live instead?
9. Nothing was deployed, yet enterprise SSO broke fleet-wide on a Tuesday morning. Which
   cookie attribute was involved, and what makes cookie attributes different from every other
   contract in this module (who enforces them)?
10. When is `X-Forwarded-For` trustworthy? Answer in terms of connections, not headers.
11. Fill in the header contract: `429`/`503` carry ______; `401` carries ______; `405`
    carries ______; `201` carries ______.
12. Classify GET, HEAD, PUT, DELETE, POST, PATCH by safety and idempotency. Which guarantee
    do automatic retries require, and why is PATCH the odd one out?
13. *Mini coding challenge.* Sketch (pseudo-code is fine) the CI test asserting that no
    state-changing route is registered on GET or HEAD. What do you iterate over?
14. Your path is browser → CDN → ALB → nginx → uvicorn. Which two module-01 invariants must
    hold at *every consecutive pair* of hops in that chain?
15. What is `Vary` actually for? Answer using the phrase "cache key".
16. Six of this module's ten incidents produced **no errors and no alerts**. Name the
    recurring diagnostic move that caught them anyway, and give two concrete vantage-point
    pairs from the incidents.
17. *Design prompt.* Design the edge for `api.ledgerly.com` from scratch: TLS certificate
    files, proxy-header trust, keep-alive ordering, CORS policy, cache policy for
    authenticated responses, and method discipline. For each decision, name the incident in
    this module it prevents.

---

## Answers

1. `Retry-After` on the `429` (01.3). Retry libraries honour it when present; absent, and
   with no backoff configured, the client's wait is zero — status codes and their headers are
   branch instructions for the caller's retry logic.
2. `cert.pem` (leaf only) served instead of `fullchain.pem` (01.8). Browsers fetch missing
   intermediates via AIA or have them cached; strict machine clients don't. Never validate
   TLS with a browser.
3. Safety: GET must have no state-changing effect (01.2). The promise is made to
   *infrastructure you will never meet* — link previewers, crawlers, prefetchers — not to
   your users.
4. `client keep-alive < proxy idle timeout < server keep-alive` (01.7): each upstream must
   hold connections longer than its downstream will reuse them, or the reuser races the
   closer.
5. `Cache-Control: private` (or `no-store`) on authenticated responses, and correct `Vary`
   so credentialed variants never share a cache entry (01.4). The CI invariant: every
   authenticated response carries `private` or `no-store`.
6. In the kernel accept queue, before the app ever saw the request (01.1) — a blocking call
   stalled the loop, connections queued in the listen backlog, and app-side timers only start
   after `accept`. Measure latency at two points; the discrepancy is the signal.
7. The Same-Origin Policy blocks cross-origin reads *by default*; CORS selectively re-allows
   them (01.9). `allow_origin_regex=".*"` + `allow_credentials=True` re-allows every origin
   *with the user's cookies* — any website can read logged-in users' data.
8. Stateless: *any replica can serve any request* (01.6) — no correctness dependency on
   process-local memory. Cross-request state lives in shared stores (DB, Redis) that all
   replicas see.
9. `SameSite=Lax` rejected at `Set-Cookie` time on the IdP's cross-site POST to `/sso/acs`
   (01.5). Cookies are enforced by the *browser* — software you neither deploy nor version,
   which can change behaviour under you on its own schedule.
10. Only as far as the proxy chain is under your control: trust is a property of the
    *connection* (which peer connected), never of the header (01.10). Trust `X-Forwarded-*`
    only from your own proxies' CIDR — `--forwarded-allow-ips="*"` lets any client spoof it.
11. `Retry-After` · `WWW-Authenticate` · `Allow` · `Location` (01.3).
12. Safe: GET, HEAD. Idempotent but unsafe: PUT, DELETE. Neither: POST. PATCH is *not
    guaranteed* idempotent — it depends on the patch semantics (01.2). Automatic retries
    require idempotency; retrying POST needs an idempotency key (02.8).
13. Iterate the app's route table; for every route whose handler mutates state (or simply:
    every non-read route), assert its methods exclude GET/HEAD (01.2). The point: the
    invariant is checkable mechanically, so it never depends on review memory.
14. The keep-alive inequality (01.7) and the forwarded-header trust rule — each hop only
    trusts `X-Forwarded-*` from the specific peer in front of it (01.10).
15. `Vary` names the request headers that join the URL in the **cache key** (01.4); without
    it, variants negotiated per-user or per-encoding collide into one cached entry.
16. Compare two vantage points and treat the *discrepancy* as the signal (module recap):
    edge latency vs app histogram (01.1), LB request count vs app count (01.7), browser vs
    clean-trust-store client (01.8), one replica vs many (01.6).
17. Shape of a strong answer: `fullchain.pem` (01.8); trust `X-Forwarded-*` only from the
    LB/nginx CIDR (01.10); client < CDN/ALB < uvicorn keep-alive (01.7); explicit CORS origin
    list, no regex, credentials only with exact origins (01.9); `private`/`no-store` +
    correct `Vary` on authenticated responses (01.4); no state-changing GET/HEAD, enforced in
    CI (01.2); the 01.3 header contract on every error path.
