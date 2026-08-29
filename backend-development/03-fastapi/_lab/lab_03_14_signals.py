"""Lab for 03.14 Production deployment — the signal/drain transcripts.

Reproduces the notebook's captured transcripts:
  A. uvicorn --workers 2: per-worker lifespan, supervisor restart, signal fan-out
  B. graceful drain: an in-flight 4s request completes after the stop signal
  C. --timeout-graceful-shutdown 2 guillotining a 30s request (CancelledError → 500)

Run:  python lab_03_14_signals.py
Platform notes: on Linux/macOS the stop signal is SIGTERM (exactly what a deploy
sends). On Windows it is CTRL_BREAK_EVENT (uvicorn's SIGBREAK handler — same code
path); Windows console events are console-scoped, so run this from its own console
window, not inside a shell you care about (PowerShell's debugger reacts to Break).
"""
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

import httpx

SCRATCH = Path(__file__).parent
IS_WIN = sys.platform == "win32"
FLAGS = subprocess.CREATE_NEW_PROCESS_GROUP if IS_WIN else 0
if IS_WIN:
    signal.signal(signal.SIGBREAK, signal.SIG_IGN)   # don't die to our own break event


def graceful_stop(proc: subprocess.Popen) -> None:
    """What a deploy does: SIGTERM (POSIX) / CTRL_BREAK_EVENT (Windows)."""
    proc.send_signal(signal.CTRL_BREAK_EVENT if IS_WIN else signal.SIGTERM)


def run_server(args: list[str]) -> tuple[subprocess.Popen, list[str]]:
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "lab_03_14_app:app", "--port", args[0], *args[1:]],
        cwd=SCRATCH, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", creationflags=FLAGS,
    )
    lines: list[str] = []
    t0 = time.monotonic()

    def pump() -> None:
        for line in proc.stdout:
            lines.append(f"t={time.monotonic() - t0:5.2f}s  {line.rstrip()}")

    threading.Thread(target=pump, daemon=True).start()
    return proc, lines


def wait_ready(port: str, tries: int = 40) -> None:
    for _ in range(tries):
        try:
            httpx.get(f"http://127.0.0.1:{port}/v1/ping", timeout=2)
            return
        except Exception:
            time.sleep(0.5)
    raise RuntimeError(f"server on {port} never became ready")


def experiment_a() -> None:
    print("=" * 72)
    print("A. uvicorn --workers 2: startup + signal + shutdown")
    proc, lines = run_server(["8141", "--workers", "2"])
    try:
        wait_ready("8141")
        pids = [httpx.get("http://127.0.0.1:8141/v1/ping").json() for _ in range(6)]
        print(f"six /v1/ping responses: {pids}")
        graceful_stop(proc)
        proc.wait(timeout=15)
        time.sleep(0.5)
        print(f"exit code: {proc.returncode}")
    finally:
        print("\n".join(lines))
        if proc.poll() is None:
            proc.kill()


def experiment_b() -> None:
    print("=" * 72)
    print("B. drain: signal arrives at t~1s of a 4s in-flight request")
    proc, lines = run_server(["8142"])
    wait_ready("8142")
    result: dict = {}

    def call() -> None:
        t0 = time.monotonic()
        try:
            r = httpx.get("http://127.0.0.1:8142/v1/slow", timeout=30)
            result["outcome"] = f"HTTP {r.status_code} {r.json()} after {time.monotonic()-t0:.1f}s"
        except Exception as e:
            result["outcome"] = f"{type(e).__name__}: {e} after {time.monotonic()-t0:.1f}s"

    th = threading.Thread(target=call)
    th.start()
    time.sleep(1.0)
    sig_at = time.monotonic()
    graceful_stop(proc)
    th.join()
    proc.wait(timeout=20)
    print(f"client outcome: {result['outcome']}")
    print(f"server exited {time.monotonic()-sig_at:.1f}s after the signal, code {proc.returncode}")
    print("\n".join(lines))


def experiment_c() -> None:
    print("=" * 72)
    print("C. --timeout-graceful-shutdown 2 vs a 30s in-flight request")
    proc, lines = run_server(["8143", "--timeout-graceful-shutdown", "2"])
    wait_ready("8143")
    result: dict = {}

    def call() -> None:
        t0 = time.monotonic()
        try:
            r = httpx.get("http://127.0.0.1:8143/v1/very-slow", timeout=40)
            result["outcome"] = f"HTTP {r.status_code} after {time.monotonic()-t0:.1f}s"
        except Exception as e:
            result["outcome"] = f"{type(e).__name__} after {time.monotonic()-t0:.1f}s"

    th = threading.Thread(target=call)
    th.start()
    time.sleep(1.0)
    sig_at = time.monotonic()
    graceful_stop(proc)
    th.join()
    proc.wait(timeout=20)
    print(f"client outcome: {result['outcome']}")
    print(f"server exited {time.monotonic()-sig_at:.1f}s after the signal, code {proc.returncode}")
    print("\n".join(lines))


if __name__ == "__main__":
    experiment_a()
    experiment_b()
    experiment_c()
