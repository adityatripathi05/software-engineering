# Module 04 lab

Runnable scripts that reproduce the notebooks' captured transcripts (AUTHORING-GUIDE §4.4).
Run each with plain `python <script>.py`; server-based sections start and stop their own
uvicorn.

| Script | Notebook | Reproduces |
|---|---|---|
| `lab_04_01_event_loop.py` | 04.1 | Task interleaving on one thread · the lag law measured (lag ≈ tasks × slice) · debug mode naming a 50 ms slice · a bystander `/ping` taxed by big-page serialisation, restored by the page cap (uvicorn, port 8175) |
| `lab_04_02_blocking.py` | 04.2 | The three tiers measured against a real 2 s provider: shared-client await (4 ms bystander) vs per-request `AsyncClient` (~380 ms hidden sync SSL build) vs sync-in-async (full freeze) · `faulthandler.dump_traceback_later` naming the frozen frame (`httpcore/_backends/sync.py … read`) · the sampler's gap-then-giant-sample view of a freeze · the import guard (uvicorn 8177, provider 8176) |
