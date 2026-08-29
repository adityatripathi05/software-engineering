"""Lab for 02.6 Filtering, sorting, searching.

Reproduces the incident's cost mechanism with sqlite and real timings: a
client-supplied sort column with no index forces a full sort of the table on
every request; the indexed column reads rows in index order. Then the closed
registry that makes every sortable field a deliberate, indexed commitment.
"""
import sqlite3
import time

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE invoices (id INTEGER PRIMARY KEY, created_at INTEGER, notes TEXT)")
db.executemany("INSERT INTO invoices VALUES (?, ?, ?)",
               [(i, i, f"note-{i * 2654435761 % 1_000_003:07d} " * 8)
                for i in range(300_000)])
db.execute("CREATE INDEX ix_invoices_created ON invoices (created_at)")
db.commit()


def timed_sort(column: str) -> float:
    t0 = time.perf_counter()
    db.execute(f"SELECT id FROM invoices ORDER BY {column} DESC LIMIT 50").fetchall()
    return (time.perf_counter() - t0) * 1000


plan_notes = db.execute("EXPLAIN QUERY PLAN SELECT id FROM invoices "
                        "ORDER BY notes DESC LIMIT 50").fetchall()
plan_created = db.execute("EXPLAIN QUERY PLAN SELECT id FROM invoices "
                          "ORDER BY created_at DESC LIMIT 50").fetchall()

print("300,000 invoices; the client asks for 50 rows, sorted:")
print(f"  ?sort=created_at (indexed) : {timed_sort('created_at'):8.1f} ms   "
      f"plan: {plan_created[0][3]}")
print(f"  ?sort=notes (NO index)     : {timed_sort('notes'):8.1f} ms   "
      f"plan: {plan_notes[0][3]}")
print("=> the unindexed sort materialises and sorts the whole table for 50 rows —")
print("   at production scale, a 2.3 GB disk sort per request, for every tenant (02.6)\n")

SORTABLE: dict[str, str] = {          # the closed registry: field -> index that backs it
    "created_at": "ix_invoices_created",
    "id": "PRIMARY KEY",
}


def order_by(client_sort: str) -> str:
    if client_sort not in SORTABLE:
        raise ValueError(f"422: sort={client_sort!r} is not a sortable field "
                         f"(sortable: {sorted(SORTABLE)})")
    return f"ORDER BY {client_sort} DESC"


print("the registry in action:")
print("  ?sort=created_at ->", order_by("created_at"))
try:
    order_by("notes")
except ValueError as e:
    print("  ?sort=notes      ->", e)
print("\n=> every sortable field is a standing index commitment: the registry pins")
print("   the public contract to the physical index that honours it (02.6).")
