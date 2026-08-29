"""Lab for 01.7 Connection lifecycle.

Reproduces the phantom-502 race with a raw socket: the server holds keep-alive
for 2s; a client that reuses the connection AFTER that window writes a request
into a socket the server has already closed — and gets nothing back. Reuse
inside the window works. The inequality follows: the reuser's idle window must
be shorter than the closer's.

Run:  python lab_01_07_keepalive.py     (starts uvicorn on port 8167, self-driving)
"""
import socket
import subprocess
import sys
import time
from pathlib import Path

from fastapi import FastAPI

app = FastAPI()


@app.get("/v1/ping")
async def ping() -> dict[str, bool]:
    return {"ok": True}


REQUEST = b"GET /v1/ping HTTP/1.1\r\nHost: 127.0.0.1:8167\r\nConnection: keep-alive\r\n\r\n"


def request_on(sock: socket.socket) -> str:
    try:
        sock.sendall(REQUEST)
        sock.settimeout(3)
        data = sock.recv(4096)
        if not data:
            return "EMPTY READ — server had already closed this connection"
        return data.split(b"\r\n", 1)[0].decode()
    except (ConnectionResetError, ConnectionAbortedError) as e:
        return f"{type(e).__name__} — the phantom failure a proxy reports as 502"
    except socket.timeout:
        return "timeout"


def drive() -> None:
    import httpx

    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "lab_01_07_keepalive:app",
         "--port", "8167", "--timeout-keep-alive", "2"],
        cwd=Path(__file__).parent, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(40):
            try:
                httpx.get("http://127.0.0.1:8167/v1/ping", timeout=2)
                break
            except Exception:
                time.sleep(0.5)

        print("server: uvicorn --timeout-keep-alive 2   (the 'downstream closer')\n")
        for idle in (1.0, 3.0):
            s = socket.create_connection(("127.0.0.1", 8167))
            first = request_on(s)
            time.sleep(idle)
            second = request_on(s)
            s.close()
            print(f"reuse after {idle:.0f}s idle:  first={first!r}")
            print(f"{'':22}second={second!r}\n")

        print("=> inside the window the connection is reusable; past it, the request")
        print("   is written into a closing socket. With an LB holding 60s in front of")
        print("   a 5s server, every reuse in the gap is a dice roll — 0.2% phantom")
        print("   502s for eleven days. Invariant: client < proxy < server (01.7).")
    finally:
        proc.kill()


if __name__ == "__main__":
    drive()
