# Module 03 lab

Runnable scripts that reproduce the notebooks' captured transcripts (AUTHORING-GUIDE §4.4).
Run them, break them, rerun them — every claim in a notebook backed by a transcript can be
checked here. All scripts run on the pinned stack with no infrastructure; run each with
plain `python <script>.py`.

| Script | Notebook | Reproduces |
|---|---|---|
| `lab_03_01_asgi.py` | 03.1 | `add_middleware` wrapping order (last added = outermost) · the route table |
| `lab_03_02_routing.py` | 03.2 | Route shadowing (first-wins matching) · the shadowed route still in OpenAPI · the fix |
| `lab_03_03_models.py` | 03.3 | `response_model` as serialisation filter · `ResponseValidationError` (contract guarded both ways) · `extra="forbid"` on input |
| `lab_03_04_pydantic.py` | 03.4 | Lax coercion admitting string→float · binary float error vs `Decimal` money · `strict=True` |
| `lab_03_05_dependencies.py` | 03.5 | Yield-dependency teardown running AFTER the response is produced |
| `lab_03_06_threadpool.py` | 03.6 | `def` vs `async` execution (worker thread vs loop) · the shared 40-token threadpool budget |
| `lab_03_07_middleware.py` | 03.7 | Last-added-outermost via enter/exit recording · middleware exceptions bypassing typed handlers |
| `lab_03_08_exceptions.py` | 03.8 | One handler on *Starlette's* HTTPException catching FastAPI's · `RequestValidationError` → problem body · `TaskGroup`/`ExceptionGroup` wrapping |
| `lab_03_09_lifespan.py` | 03.9 | The `with TestClient` lifecycle vs the bare-client fixture trap · yielded state as `request.state` · supervised-task cancellation re-raise |
| `lab_03_10_backgroundtasks.py` | 03.10 | Task runs after the response · a crashing task invisible to the 200 the client holds · at-most-once, unrecorded |
| `lab_03_11_streaming.py` | 03.11 | Backpressure: the streaming generator paced by the client's reads once buffers fill (real uvicorn, port 8151) |
| `lab_03_12_websockets.py` | 03.12 | Frameless drop → client-synthesised 1006 · explicit `close(4400)` · pre-accept `WebSocketException`: 1008 in-process vs HTTP 403 on the wire (real uvicorn, port 8152) |
| `lab_03_13_openapi.py` | 03.13 | Default operationIds · the `openapi()` cache · declared `responses` and the auto-422 · docs gating · `-Input`/`-Output` split · duplicate-name guard · 422 override · router-level merge |
| `lab_03_14_app.py` + `lab_03_14_signals.py` + `lab_03_14_rootpath.py` | 03.14 | Per-worker lifespan and supervisor restart · graceful drain of an in-flight request · `--timeout-graceful-shutdown` expiry · `root_path` behind a prefix-stripping proxy (real uvicorn, ports 8141–8143) |

⚠️ `lab_03_14_signals.py` stops real uvicorn processes with real signals (SIGTERM on POSIX,
CTRL_BREAK on Windows). On Windows, run it from its own console window — console break
events are console-scoped.

Provenance: labs for 03.13–03.14 are the original transcript-producing harnesses; labs for
03.1–03.12 were re-derived from the notebooks' captures after the §4.4 convention was adopted,
and each was verified to reproduce its notebook's behaviour on the pinned stack. That
verification caught one transport nuance now documented in 03.12's Version note (pre-accept
`WebSocketException`: close 1008 in-process, HTTP 403 over a real socket).
