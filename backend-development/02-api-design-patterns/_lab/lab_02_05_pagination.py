"""Lab for 02.5 Pagination.

Reproduces the export incident with sqlite: an exporter walks OFFSET pages over
`created_at DESC` while invoices keep being created. The lab measures what a
changing list does to offset positions — rows re-served and rows never seen —
then runs the same export with a keyset cursor `(created_at, id)` and compares.
"""
import sqlite3

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE invoices (id INTEGER PRIMARY KEY, created_at INTEGER)")
NEXT = {"id": 0, "t": 0}


def create_invoices(n: int) -> None:
    for _ in range(n):
        NEXT["id"] += 1
        NEXT["t"] += 1
        db.execute("INSERT INTO invoices VALUES (?, ?)", (NEXT["id"], NEXT["t"]))


create_invoices(100)                       # the month's invoices at export start
PAGE = 10


def export_offset() -> list[int]:
    seen, page = [], 0
    while True:
        rows = db.execute(
            "SELECT id FROM invoices ORDER BY created_at DESC, id DESC "
            "LIMIT ? OFFSET ?", (PAGE, page * PAGE)).fetchall()
        if not rows:
            return seen
        seen += [r[0] for r in rows]
        create_invoices(3)                 # writes continue between page reads
        page += 1


def export_cursor() -> list[int]:
    seen, cursor = [], (float("inf"), float("inf"))
    while True:
        rows = db.execute(
            "SELECT id, created_at FROM invoices WHERE (created_at, id) < (?, ?) "
            "ORDER BY created_at DESC, id DESC LIMIT ?", (*cursor[::-1], PAGE)).fetchall()
        if not rows:
            return seen
        seen += [r[0] for r in rows]
        cursor = (rows[-1][0], rows[-1][1])    # (id, created_at) of the last row
        create_invoices(3)


def report(label: str, ids: list[int]) -> None:
    start_set = set(range(1, 101))
    during = set(range(101, NEXT["id"] + 1))          # created while exporting
    print(f"{label}: {len(ids)} rows fetched, table ended at {NEXT['id']} rows")
    print(f"  duplicates re-served               : {len(ids) - len(set(ids))}")
    print(f"  start-set rows never seen          : {sorted(start_set - set(ids)) or 'none'}")
    print(f"  created-during-export rows missed  : {len(during - set(ids))} of {len(during)}")


ids = export_offset()
report("OFFSET export while writes continue", ids)

db.execute("DELETE FROM invoices")
NEXT["id"] = NEXT["t"] = 0
create_invoices(100)
ids2 = export_cursor()
report("\nCURSOR export, same write traffic", ids2)

print("\n=> position-by-counting has no stable answer over a changing list;")
print("   a keyset cursor names a ROW, not a position, so the walk is exact")
print("   for everything at-or-before its starting point (02.5).")
