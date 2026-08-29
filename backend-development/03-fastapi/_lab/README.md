# Module 03 lab

Runnable scripts that reproduce the notebooks' captured transcripts (AUTHORING-GUIDE §4.4).
Run them, break them, rerun them — every claim in a notebook backed by a transcript can be
checked here. All scripts run on the pinned stack with no infrastructure.

| Script | Notebook | Reproduces |
|---|---|---|
| `lab_03_13_openapi.py` | 03.13 | Default operationIds · the `openapi()` cache · declared `responses` and the auto-422 · docs gating (`docs_url=None` vs `openapi_url=None`) · `-Input`/`-Output` split + opt-out · duplicate-name guard · 422 override · router-level `responses` merge |
| `lab_03_14_app.py` | 03.14 | The app driven by the signals lab (per-worker lifespan prints, 4 s and 30 s routes) |
| `lab_03_14_signals.py` | 03.14 | Multiprocess startup and per-worker lifespan · supervisor worker restart · graceful drain of an in-flight request · `--timeout-graceful-shutdown` expiry (CancelledError → 500) |
| `lab_03_14_rootpath.py` | 03.14 | `root_path` behind a prefix-stripping proxy (`servers` in the OpenAPI document) |

Run each with plain `python <script>.py`.

⚠️ `lab_03_14_signals.py` starts real uvicorn processes on ports 8141–8143 and stops them
with real signals (SIGTERM on POSIX, CTRL_BREAK on Windows). On Windows, run it from its
own console window — console break events are console-scoped.

Notebooks 03.1–03.12 predate this convention (their transcripts were produced the same way,
but the harnesses were not preserved). Labs are complete from 03.13 onward.
