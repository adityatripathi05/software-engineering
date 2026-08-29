"""Lab for 01.3 Status codes and headers.

Reproduces the incident with the REAL client library from the story: urllib3's
Retry honours Retry-After when present; with the header absent and
backoff_factor=0, its wait is ZERO — a polite retry policy becomes a tight
loop. The server-side hit timestamps are the proof.

Run:  python lab_01_03_retry_after.py     (starts uvicorn on port 8163, self-driving)
"""
import subprocess
import sys
import time
from pathlib import Path

from fastapi import FastAPI, Response

app = FastAPI()
HITS: dict[str, list[float]] = {"with": [], "without": []}
T0 = time.monotonic()


@app.get("/v1/limited-with-header")
async def limited_with(response: Response) -> Response:
    HITS["with"].append(time.monotonic() - T0)
    return Response(status_code=429, headers={"Retry-After": "1"})


@app.get("/v1/limited-no-header")
async def limited_without() -> Response:
    HITS["without"].append(time.monotonic() - T0)
    return Response(status_code=429)          # the refactor dropped the header


@app.get("/v1/hits")
async def hits() -> dict[str, list[float]]:
    return HITS


def drive() -> None:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "lab_01_03_retry_after:app", "--port", "8163"],
        cwd=Path(__file__).parent, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(40):
            try:
                requests.get("http://127.0.0.1:8163/v1/hits", timeout=2)
                break
            except Exception:
                time.sleep(0.5)

        # the customer's exact configuration: 5 retries, no backoff_factor
        s = requests.Session()
        s.mount("http://", HTTPAdapter(max_retries=Retry(
            total=5, status_forcelist=[429], backoff_factor=0,
            respect_retry_after_header=True)))

        for path in ("limited-no-header", "limited-with-header"):
            t0 = time.monotonic()
            try:
                s.get(f"http://127.0.0.1:8163/v1/{path}", timeout=30)
            except requests.exceptions.RetryError:
                pass
            print(f"/{path}: retries exhausted in {time.monotonic()-t0:5.2f}s")

        hits = requests.get("http://127.0.0.1:8163/v1/hits", timeout=5).json()
        for key, label in (("without", "Retry-After ABSENT "), ("with", "Retry-After: 1     ")):
            spacing = [f"{b - a:.2f}s" for a, b in zip(hits[key], hits[key][1:])]
            print(f"{label} -> {len(hits[key])} hits, spaced {spacing}")
        print("\n=> same client, same policy: the header IS the client's wait —")
        print("   drop it and 8 worker threads x 5 retries becomes a flood (01.3).")
    finally:
        proc.kill()


if __name__ == "__main__":
    drive()
