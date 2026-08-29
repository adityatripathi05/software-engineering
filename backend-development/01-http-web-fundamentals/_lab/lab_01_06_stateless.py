"""Lab for 01.6 Stateless vs stateful.

Reproduces the incident with real processes: an idempotency guard kept in a
module-level dict exists PER PROCESS — under `--workers 2`, the same key sent
repeatedly creates an invoice on EACH worker that sees it first. The pid in
every response is the proof.

Run:  python lab_01_06_stateless.py     (starts uvicorn --workers 2 on port 8166)
"""
import os
import subprocess
import sys
import time
from pathlib import Path

from fastapi import FastAPI, Header, Response

app = FastAPI()
_seen: dict[str, str] = {}          # ⚠️ the guard from the incident: per-process memory


@app.post("/v1/invoices")
async def create_invoice(response: Response,
                         idempotency_key: str = Header()) -> dict[str, str | int]:
    if idempotency_key in _seen:
        return {"pid": os.getpid(), "invoice": _seen[idempotency_key], "replay": 1}
    invoice_id = f"inv_{os.getpid()}_{len(_seen)}"
    _seen[idempotency_key] = invoice_id
    response.status_code = 201
    return {"pid": os.getpid(), "invoice": invoice_id, "replay": 0}


def drive() -> None:
    import httpx

    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "lab_01_06_stateless:app",
         "--port", "8166", "--workers", "2"],
        cwd=Path(__file__).parent, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(60):
            try:
                httpx.post("http://127.0.0.1:8166/v1/invoices",
                           headers={"Idempotency-Key": "warmup"}, timeout=2)
                break
            except Exception:
                time.sleep(0.5)

        created: dict[str, set[str]] = {}
        pids: set[int] = set()
        for _ in range(40):          # same key, over and over — one client retrying
            with httpx.Client() as fresh:            # new connection → may hit either worker
                r = fresh.post("http://127.0.0.1:8166/v1/invoices",
                               headers={"Idempotency-Key": "invoice-001"}, timeout=5)
            body = r.json()
            pids.add(body["pid"])
            if not body["replay"]:
                created.setdefault("invoice-001", set()).add(body["invoice"])

        dupes = created.get("invoice-001", set())
        print(f"workers that answered: {sorted(pids)}")
        print(f"invoices created for ONE idempotency key: {sorted(dupes)}")
        if len(dupes) > 1:
            print("=> each worker's dict was sure it checked first: duplicate invoices.")
        else:
            print("(all requests landed on one worker this run — rerun to see the race;")
            print(" accept() is contested, not balanced — 03.14)")
        print("\n=> stateless means ANY replica can serve ANY request: cross-request")
        print("   state lives in a shared store all replicas see, never in a dict (01.6).")
    finally:
        proc.kill()


if __name__ == "__main__":
    drive()
