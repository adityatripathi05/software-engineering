# Module 01 lab

Runnable scripts that reproduce the notebooks' incident mechanisms (AUTHORING-GUIDE §4.4).
Run each with plain `python <script>.py`; no infrastructure needed — the server-based ones
start and stop their own uvicorn (ports 8161–8171).

| Script | Notebook | Reproduces |
|---|---|---|
| `lab_01_01_lifecycle.py` | 01.1 | One sync call inside `async def` serialising the worker — concurrent requests queue, a bystander `/ping` takes ~1.8 s |
| `lab_01_02_methods.py` | 01.2 | A state-changing GET executed by every "preview" fetch · PUT vs POST idempotency · the no-mutating-GET route guard |
| `lab_01_03_retry_after.py` | 01.3 | The retry storm, with the real client (`requests` + `urllib3.Retry`): hits spaced 0.00 s without `Retry-After`, 1.00 s with it |
| `lab_01_04_caching.py` | 01.4 | A shared cache's storability rule: `max-age` without `private` serves tenant A's invoices to tenant B; `private` refuses |
| `lab_01_05_cookies.py` | 01.5 | The Set-Cookie attribute contract (server's half). ⚠️ `SameSite` acceptance/rejection is browser-enforced — not reproducible with an HTTP library, which is the notebook's point |
| `lab_01_06_stateless.py` | 01.6 | Real duplicate invoices: one idempotency key, `--workers 2`, a per-process `_seen` dict — each pid creates its own |
| `lab_01_07_keepalive.py` | 01.7 | The phantom-502 race on a raw socket: reuse inside the keep-alive window works; past it, the request lands in a closing socket |
| `lab_01_08_tls.py` | 01.8 | A real generated chain (root → intermediate → leaf): serving `cert.pem` fails a strict client (`unable to get local issuer certificate`); `fullchain.pem` handshakes TLSv1.3 |
| `lab_01_09_cors.py` | 01.9 | `allow_origin_regex=".*"` + credentials reflecting `evil.example` with `allow-credentials: true` vs the explicit-list preflight |
| `lab_01_10_forwarded.py` | 01.10 | `forwarded_allow_ips="*"` letting a direct caller spoof IP and scheme; a restricted CIDR ignoring the same headers |

Provenance: these labs were re-derived from the notebooks' incidents after the §4.4
convention was adopted (the original harnesses were not preserved), and each was verified on
the pinned stack. Two Windows-specific notes: `lab_01_10` starts uvicorn programmatically
because click (uvicorn's CLI) expands a bare `*` argument to filenames on Windows; browser-only
behaviour (01.5 SameSite enforcement) is documented rather than simulated.
