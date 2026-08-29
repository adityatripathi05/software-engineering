"""Lab for 01.10 Reverse proxies and forwarded headers.

Reproduces the incident's mechanism: with `forwarded_allow_ips="*"`, ANY peer's
X-Forwarded-For/Proto rewrite what the app believes about the client — a direct
caller spoofs its IP and scheme. With trust restricted to a CIDR the caller is
not in, the same headers are ignored.

Run:  python lab_01_10_forwarded.py     (starts uvicorn on port 8171, twice)

Implementation note: the server is started programmatically (uvicorn.run) rather
than via the CLI, because uvicorn's CLI is click-based and ⚠️ click expands a
bare `*` argument to the directory's filenames on Windows — the very flag under
test is un-passable through the CLI there.
"""
import subprocess
import sys
import time
from pathlib import Path

from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/v1/whoami")
async def whoami(request: Request) -> dict[str, str]:
    return {
        "client_ip_the_app_believes": request.client.host,
        "scheme_the_app_believes": request.url.scheme,
    }


SPOOF = {"X-Forwarded-For": "198.51.100.99", "X-Forwarded-Proto": "https"}


def serve(allow_ips: str) -> None:
    import uvicorn

    uvicorn.run("lab_01_10_forwarded:app", port=8171, log_level="warning",
                proxy_headers=True, forwarded_allow_ips=allow_ips)


def run_and_probe(allow_ips: str) -> None:
    import httpx

    proc = subprocess.Popen(
        [sys.executable, Path(__file__).name, "serve", allow_ips],
        cwd=Path(__file__).parent, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(40):
            try:
                httpx.get("http://127.0.0.1:8171/v1/whoami", timeout=2)
                break
            except Exception:
                time.sleep(0.5)
        else:
            raise RuntimeError("server never became ready")
        r = httpx.get("http://127.0.0.1:8171/v1/whoami", headers=SPOOF, timeout=5)
        print(f"forwarded_allow_ips={allow_ips!r}")
        print(f"  direct client (127.0.0.1) sends {SPOOF}")
        print(f"  app believes: {r.json()}\n")
    finally:
        proc.kill()
        time.sleep(0.5)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        serve(sys.argv[2])
    else:
        run_and_probe("*")               # the incident's flag: trust ANYONE's headers
        run_and_probe("203.0.113.7")     # trust only a proxy the caller is not
        print("=> trust is a property of the CONNECTION (which peer connected), never of")
        print("   the header. With '*', an attacker chooses their own IP in your logs and")
        print("   fraud rules — 2.1M login attempts, 3 rejections (01.10). The CIDR is")
        print("   deployment config with a CI assertion (03.14).")
