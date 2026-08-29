"""Lab for 03.11 File uploads and streaming responses.

Reproduces the backpressure capture: a StreamingResponse generator is paced by
the CLIENT's read speed — whatever the generator holds (in the incident, a
pooled DB connection) is held for the client's pace, not the server's.

Run:  python lab_03_11_streaming.py     (starts uvicorn on port 8151, self-driving)
"""
import subprocess
import sys
import threading
import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()
CHUNK = b"x" * (4 * 1024 * 1024)     # 4 MiB per yield — bigger than the transport buffers,
                                     # so the generator genuinely BLOCKS on a slow reader


@app.get("/v1/statements/lines.csv")
async def stream_lines() -> StreamingResponse:
    def rows():
        t0 = time.monotonic()
        for i in range(10):
            print(f"[server] yield chunk {i} at t={time.monotonic()-t0:4.1f}s "
                  f"(imagine conn #7 still checked out)", flush=True)
            yield CHUNK
        print(f"[server] generator done at t={time.monotonic()-t0:4.1f}s", flush=True)
    return StreamingResponse(rows(), media_type="text/csv")


def drive() -> None:
    import httpx

    here = Path(__file__).parent
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "lab_03_11_streaming:app", "--port", "8151"],
        cwd=here, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8",
    )
    lines: list[str] = []
    threading.Thread(target=lambda: [lines.append(l.rstrip()) for l in proc.stdout],
                     daemon=True).start()
    try:
        for _ in range(40):
            try:
                httpx.get("http://127.0.0.1:8151/openapi.json", timeout=2)
                break
            except Exception:
                time.sleep(0.5)
        t0 = time.monotonic()
        read = 0
        with httpx.stream("GET", "http://127.0.0.1:8151/v1/statements/lines.csv",
                          timeout=60) as r:
            for _chunk in r.iter_bytes(chunk_size=256 * 1024):
                read += len(_chunk)
                if read % (4 * 1024 * 1024) < 256 * 1024:
                    print(f"[client] ~{read // (1024*1024):2d} MiB read at "
                          f"t={time.monotonic()-t0:4.1f}s (throttled reader)")
                time.sleep(0.1)          # the slow consumer: ~2.5 MiB/s
    finally:
        proc.kill()
        time.sleep(0.3)
    print("\n[server log]")
    print("\n".join(l for l in lines if "[server]" in l))
    print("\n=> the first yields vanish into transport buffers (generous on loopback);")
    print("   once they fill, every further yield WAITS for the client's reads — the")
    print("   generator, and everything it holds (the pooled connection), is on a")
    print("   client-paced loan. Buffers only defer the loan; they never repay it (03.11).")


if __name__ == "__main__":
    drive()
