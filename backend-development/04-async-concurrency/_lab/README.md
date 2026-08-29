# Module 04 lab

Runnable scripts that reproduce the notebooks' captured transcripts (AUTHORING-GUIDE §4.4).
Run each with plain `python <script>.py`; server-based sections start and stop their own
uvicorn.

| Script | Notebook | Reproduces |
|---|---|---|
| `lab_04_01_event_loop.py` | 04.1 | Task interleaving on one thread · the lag law measured (lag ≈ tasks × slice) · debug mode naming a 50 ms slice · a bystander `/ping` taxed by big-page serialisation, restored by the page cap (uvicorn, port 8175) |
