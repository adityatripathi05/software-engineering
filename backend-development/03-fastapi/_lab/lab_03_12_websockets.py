"""Lab for 03.12 WebSockets basics.

Reproduces the close-code captures over a REAL socket (TestClient cannot show a
frameless TCP drop):
  /ws/strict   — unhandled exception after accept() → NO close frame; the client
                 library reports 1006 (abnormal closure), a code nobody sent
  /ws/tolerant — explicit close(4400, reason) → the client KNOWS the verdict
  handshake    — a dependency raising WebSocketException(1008): TestClient (in-
                 process) delivers close code 1008 — but over a REAL uvicorn
                 socket the pre-accept rejection arrives as an HTTP 403 handshake
                 denial, because before accept() there is no socket to close.
                 This lab shows BOTH transports side by side.

Run:  python lab_03_12_websockets.py     (starts uvicorn on port 8152, self-driving)
"""
import asyncio
import subprocess
import sys
import time
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, WebSocket, WebSocketException
from pydantic import BaseModel, ConfigDict, ValidationError

app = FastAPI()


class Subscribe(BaseModel):
    model_config = ConfigDict(extra="forbid")     # the incident's strict model
    type: str
    operation_id: str


async def require_token(ws: WebSocket) -> str:
    token = ws.query_params.get("token")
    if token != "key_live_7ac":
        raise WebSocketException(code=1008, reason="invalid credentials")
    return token


@app.websocket("/ws/strict")
async def strict_feed(ws: WebSocket) -> None:
    await ws.accept()
    raw = await ws.receive_json()
    Subscribe.model_validate(raw)          # raises on the extra field → frameless drop
    await ws.send_json({"subscribed": True})


@app.websocket("/ws/tolerant")
async def tolerant_feed(ws: WebSocket) -> None:
    await ws.accept()
    raw = await ws.receive_json()
    try:
        Subscribe.model_validate({k: raw[k] for k in ("type", "operation_id") if k in raw})
        await ws.send_json({"subscribed": True})
    except (ValidationError, KeyError):
        await ws.close(code=4400, reason="unrecognised message; see /docs/ws")


@app.websocket("/ws/guarded")
async def guarded(ws: WebSocket, token: Annotated[str, Depends(require_token)]) -> None:
    await ws.accept()


async def drive() -> None:
    import websockets

    async def outcome(path: str, payload: str | None) -> str:
        try:
            async with websockets.connect(f"ws://127.0.0.1:8152{path}") as ws:
                if payload is not None:
                    await ws.send(payload)
                    return f"reply: {await asyncio.wait_for(ws.recv(), 5)}"
                return "connected"
        except websockets.exceptions.ConnectionClosed as e:
            frame = e.rcvd
            if frame is None or frame.code == 1006:
                return "NO close frame — abrupt TCP drop (a browser reports this as 1006)"
            return f"closed code={frame.code} reason={frame.reason!r}"
        except Exception as e:
            return f"{type(e).__name__}: {e}"

    msg = '{"type": "subscribe", "operation_id": "op_7712", "v": 1}'   # the year-old field
    print("/ws/strict  :", await outcome("/ws/strict", msg))
    print("/ws/tolerant:", await outcome("/ws/tolerant", msg))
    print("/ws/tolerant (garbage):", await outcome("/ws/tolerant", '"garbage"'))
    print("/ws/guarded (bad token), REAL socket:", await outcome("/ws/guarded?token=wrong", None))
    print("\n=> the strict handler's bug is indistinguishable from a network failure —")
    print("   which is exactly what client reconnect logic retries instantly (03.12).")


def testclient_1008() -> None:
    """The same rejection in-process: TestClient's portal delivers the 1008."""
    from fastapi.testclient import TestClient
    from starlette.websockets import WebSocketDisconnect

    try:
        with TestClient(app).websocket_connect("/ws/guarded?token=wrong"):
            pass
    except WebSocketDisconnect as e:
        print(f"/ws/guarded (bad token), TestClient : close code={e.code} reason={e.reason!r}")
    print("=> pre-accept WebSocketException: 1008 in-process, HTTP 403 on the wire —")
    print("   before accept() there is no WebSocket on the wire to close.")


def main() -> None:
    here = Path(__file__).parent
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "lab_03_12_websockets:app", "--port", "8152"],
        cwd=here, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        import httpx
        for _ in range(40):
            try:
                httpx.get("http://127.0.0.1:8152/openapi.json", timeout=2)
                break
            except Exception:
                time.sleep(0.5)
        asyncio.run(drive())
        testclient_1008()
    finally:
        proc.kill()


if __name__ == "__main__":
    main()
