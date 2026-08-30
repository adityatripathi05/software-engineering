"""Lab for 04.6 Lost updates and double writes.

Reproduces the notebook's captures with two real database connections and
deterministic interleaving (no sleeps, no luck):
  A. the lost update: two payments read-modify-write the same balance;
     one vanishes. The atomic expression fix.
  B. the state-machine race: send vs void both check status='draft';
     the void is overwritten AND the email goes out. The CAS fix
     (conditional UPDATE + rowcount) makes exactly one transition win.
  C. the double write: two scheduler replicas insert the same reminder;
     the unique constraint arbitrates (03.8's IntegrityError, by name).
  D. the version column: optimistic concurrency, rowcount as the verdict.

Run:  python lab_04_06_lost_updates.py     (sqlite, two connections, one file)
"""
import sqlite3
import tempfile
from pathlib import Path

DB = Path(tempfile.mkdtemp()) / "ledgerly.db"


def connect() -> sqlite3.Connection:
    c = sqlite3.connect(DB, isolation_level=None)   # autocommit; explicit txns
    c.execute("PRAGMA busy_timeout = 2000")
    return c


setup = connect()
setup.executescript("""
CREATE TABLE invoices (
    id TEXT PRIMARY KEY, status TEXT NOT NULL,
    paid_amount INTEGER NOT NULL DEFAULT 0, version INTEGER NOT NULL DEFAULT 1);
CREATE TABLE reminders (
    invoice_id TEXT, kind TEXT, period TEXT, sent_at TEXT,
    UNIQUE (invoice_id, kind, period));
INSERT INTO invoices (id, status) VALUES ('inv_9f2c41', 'draft');
""")

req1, req2 = connect(), connect()      # two replicas / two concurrent requests


# ---------- A. the lost update ------------------------------------------------
def section_a() -> None:
    print("A. two payments (40 + 60) applied read-modify-write")
    a = req1.execute("SELECT paid_amount FROM invoices WHERE id='inv_9f2c41'").fetchone()[0]
    b = req2.execute("SELECT paid_amount FROM invoices WHERE id='inv_9f2c41'").fetchone()[0]
    req1.execute("UPDATE invoices SET paid_amount=? WHERE id='inv_9f2c41'", (a + 40,))
    req2.execute("UPDATE invoices SET paid_amount=? WHERE id='inv_9f2c41'", (b + 60,))
    final = req1.execute("SELECT paid_amount FROM invoices WHERE id='inv_9f2c41'").fetchone()[0]
    print(f"   req-1 read {a}, wrote {a+40}; req-2 read {b}, wrote {b+60}")
    print(f"   final paid_amount: {final}   (40 is GONE — last write wins)")

    req1.execute("UPDATE invoices SET paid_amount=0 WHERE id='inv_9f2c41'")
    req1.execute("UPDATE invoices SET paid_amount = paid_amount + 40 WHERE id='inv_9f2c41'")
    req2.execute("UPDATE invoices SET paid_amount = paid_amount + 60 WHERE id='inv_9f2c41'")
    final = req1.execute("SELECT paid_amount FROM invoices WHERE id='inv_9f2c41'").fetchone()[0]
    print(f"   atomic expression (SET paid = paid + ?): final = {final}")
    print("  => the fix is moving the arithmetic INTO the write: the database")
    print("     computes on the current row, never on your photograph (04.6)\n")


# ---------- B. the state-machine race ----------------------------------------
def section_b() -> None:
    print("B. send vs void, both checking status == 'draft'")
    emails: list[str] = []

    # naive: read-check-act, interleaved exactly as the incident interleaved
    s = req1.execute("SELECT status FROM invoices WHERE id='inv_9f2c41'").fetchone()[0]
    v = req2.execute("SELECT status FROM invoices WHERE id='inv_9f2c41'").fetchone()[0]
    if v == "draft":
        req2.execute("UPDATE invoices SET status='void' WHERE id='inv_9f2c41'")
    if s == "draft":                                       # stale photograph
        req1.execute("UPDATE invoices SET status='sent' WHERE id='inv_9f2c41'")
        emails.append("invoice email to customer")
    final = req1.execute("SELECT status FROM invoices WHERE id='inv_9f2c41'").fetchone()[0]
    print(f"   naive : final status={final!r}, emails sent={emails}")
    print("           (the VOID was silently overwritten, and the email went out)")

    # CAS: the condition rides the write; rowcount is the verdict
    req1.execute("UPDATE invoices SET status='draft' WHERE id='inv_9f2c41'")
    emails.clear()
    void = req2.execute(
        "UPDATE invoices SET status='void' WHERE id='inv_9f2c41' AND status='draft'")
    send = req1.execute(
        "UPDATE invoices SET status='sent' WHERE id='inv_9f2c41' AND status='draft'")
    if send.rowcount == 1:
        emails.append("invoice email to customer")
    final = req1.execute("SELECT status FROM invoices WHERE id='inv_9f2c41'").fetchone()[0]
    print(f"   CAS   : void.rowcount={void.rowcount}, send.rowcount={send.rowcount}"
          f" -> status={final!r}, emails sent={emails or 'NONE'}")
    print("  => exactly one transition wins; the loser LEARNS it lost (rowcount 0)")
    print("     and its side effect never happens (04.6)\n")


# ---------- C. the double write ----------------------------------------------
def section_c() -> None:
    print("C. two scheduler replicas send the November overdue reminder")
    row = ("inv_9f2c41", "overdue", "2026-11", "12 Nov 03:00")
    req1.execute("INSERT INTO reminders VALUES (?,?,?,?)", row)
    print("   replica 1: INSERT ok — reminder sent")
    try:
        req2.execute("INSERT INTO reminders VALUES (?,?,?,?)", row)
    except sqlite3.IntegrityError as e:
        print(f"   replica 2: IntegrityError: {e}")
    print("  => the unique constraint is the ARBITER: the second writer gets a")
    print("     named verdict to map (03.8), not a duplicate side effect (04.6)\n")


# ---------- D. the version column --------------------------------------------
def section_d() -> None:
    print("D. optimistic concurrency: two editors, one version column")
    v1 = req1.execute("SELECT version FROM invoices WHERE id='inv_9f2c41'").fetchone()[0]
    v2 = req2.execute("SELECT version FROM invoices WHERE id='inv_9f2c41'").fetchone()[0]
    first = req1.execute(
        "UPDATE invoices SET paid_amount=paid_amount, version=version+1 "
        "WHERE id='inv_9f2c41' AND version=?", (v1,))
    second = req2.execute(
        "UPDATE invoices SET paid_amount=paid_amount, version=version+1 "
        "WHERE id='inv_9f2c41' AND version=?", (v2,))
    print(f"   both read version={v1}; first UPDATE rowcount={first.rowcount}, "
          f"second rowcount={second.rowcount}")
    print("  => rowcount 0 = 'the row moved under you': reload and retry, or")
    print("     surface it as 409/412 with ETag/If-Match (01.4, 02.x) (04.6)")


if __name__ == "__main__":
    section_a()
    section_b()
    section_c()
    section_d()
