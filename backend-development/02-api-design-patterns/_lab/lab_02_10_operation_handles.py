"""Lab for 02.10 Long-running operations.

Reproduces the amplification loop: the status endpoint reads a lagging replica,
so a freshly issued handle polls as 404; a well-written SDK treats 404 as "does
not exist" and RESUBMITS — each retry a whole new export job. Then the fix:
never hand back a handle that is not durably readable where status reads.
"""
import time

PRIMARY: dict[str, str] = {}
REPLICA: dict[str, str] = {}
REPLICA_LAG_POLLS = 2                 # replication applies after 2 poll cycles
pending_lag: list[tuple[int, str]] = []
JOBS_STARTED = {"count": 0}
POLL = {"n": 0}


def replicate() -> None:
    for due, op in list(pending_lag):
        if POLL["n"] >= due:
            REPLICA[op] = PRIMARY[op]
            pending_lag.remove((due, op))


def submit_reading_replica() -> str:
    JOBS_STARTED["count"] += 1
    op = f"op_{JOBS_STARTED['count']:04d}"
    PRIMARY[op] = "running"
    pending_lag.append((POLL["n"] + REPLICA_LAG_POLLS, op))    # visible later
    return op


def poll_replica(op: str) -> int:
    POLL["n"] += 1
    replicate()
    return 200 if op in REPLICA else 404


def sdk_export_with_retries() -> None:
    """The customer's SDK: 404 on a handle == submission failed == resubmit."""
    for attempt in range(1, 5):
        op = submit_reading_replica()
        status = poll_replica(op)
        print(f"  attempt {attempt}: submitted {op}, first poll -> {status}"
              + ("  => SDK: 'does not exist' -> resubmit" if status == 404 else ""))
        if status == 200:
            return


print("-- status endpoint reads a lagging replica --")
sdk_export_with_retries()
print(f"  40-minute export jobs actually started: {JOBS_STARTED['count']}")
print("  => each retry deepens the queue, which slows workers, which increases")
print("     lag, which produces more 404s: the amplification loop (02.10)\n")

print("-- fix: the handle is only issued once durably readable where status reads --")
JOBS_STARTED["count"] = 0


def submit_read_your_writes() -> str:
    JOBS_STARTED["count"] += 1
    op = f"op_{JOBS_STARTED['count']:04d}"
    PRIMARY[op] = "running"           # operation row + enqueue: one transaction
    return op


def poll_primary(op: str) -> int:
    return 200 if op in PRIMARY else 404


op = submit_read_your_writes()
print(f"  submitted {op}, first poll -> {poll_primary(op)}")
print(f"  jobs started: {JOBS_STARTED['count']}")
print("\n=> 404 means 'does not exist' and clients may act on that — so an id you")
print("   issued must NEVER 404. Write the operation row and the enqueue in one")
print("   transaction; read status where that write is visible (02.10).")
