"""Lab for 05.5 Indexing.

Reproduces the notebook's captures against the module compose.yaml (PostgreSQL 18):
  A. what an index buys: one row out of 410k in a handful of buffer reads
  B. the incident shape: the sparse-agent inbox forced through the wrong index -
     "Rows Removed by Filter" as the smoking number - then the purpose-built
     partial index (CREATE INDEX CONCURRENTLY), and the before/after
  C. the leftmost-prefix rule on the new composite index
  D. index-only scans and the visibility map: Heap Fetches before/after VACUUM
  E. what silently disqualifies an index: a function on the column, and the
     expression index that fixes it
  F. the write bill: HOT updates and WAL, before and after indexing a column
     you update
  G. hygiene: pg_stat_user_indexes and the just-in-case indexes nobody scans

RLS from 05.4 is deliberately NOT enabled here, to keep planner output about
indexing alone (05.4 already captured the policy qual folding into plans).

Run:  docker compose up -d --wait   (in the module directory), then
      python lab_05_05_indexing.py
"""
import asyncio
import sys
import time

import asyncpg

if sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DSN = "postgresql://deskhub:deskhub_dev@127.0.0.1:55432/deskhub"


async def wal_bytes(conn: asyncpg.Connection) -> int:
    return await conn.fetchval(
        "SELECT pg_wal_lsn_diff(pg_current_wal_insert_lsn(), '0/0')::bigint")


async def explain(conn, sql: str, *args, keys=("Index", "Filter", "Rows Removed",
                                               "Heap Fetches", "Buffers",
                                               "Execution Time", "Seq Scan", "Sort")):
    plan = await conn.fetch("EXPLAIN (ANALYZE, BUFFERS) " + sql, *args)
    for line in plan:
        text = line["QUERY PLAN"]
        if any(k in text for k in keys):
            print(f"   {text.strip()}")


# ---------- seed ---------------------------------------------------------------
async def seed(conn: asyncpg.Connection) -> tuple[str, str, str]:
    print("seeding: Nordwind at 400k tickets + 2 small tenants, 60 agents ...")
    await conn.execute("""
        DROP TABLE IF EXISTS attachments, comments, tickets, agents, tenants,
                             ticket_counters CASCADE;
        CREATE TABLE tenants (
            id uuid PRIMARY KEY DEFAULT uuidv7(), slug text NOT NULL UNIQUE);
        CREATE TABLE agents (
            id uuid PRIMARY KEY DEFAULT uuidv7(),
            tenant_id uuid NOT NULL REFERENCES tenants(id),
            email text NOT NULL, UNIQUE (tenant_id, email),
            CONSTRAINT uq_agents_tenant_id_id UNIQUE (tenant_id, id));
        CREATE TABLE tickets (
            id uuid PRIMARY KEY DEFAULT uuidv7(),
            tenant_id uuid NOT NULL REFERENCES tenants(id),
            number bigint NOT NULL,
            requester_email text NOT NULL,
            subject text NOT NULL,
            status text NOT NULL DEFAULT 'open'
                CONSTRAINT ck_tickets_status
                CHECK (status IN ('open','pending','solved','closed')),
            priority text NOT NULL DEFAULT 'normal',
            assignee_id uuid,
            comment_count int NOT NULL DEFAULT 0,
            last_activity_at timestamptz,
            UNIQUE (tenant_id, number),
            CONSTRAINT uq_tickets_tenant_id_id UNIQUE (tenant_id, id),
            CONSTRAINT fk_tickets_tenant_assignee
                FOREIGN KEY (tenant_id, assignee_id)
                REFERENCES agents (tenant_id, id))
        WITH (fillfactor = 90);   -- update-heavy table: leave room for HOT (section F)
        CREATE INDEX ix_tickets_tenant_activity
            ON tickets (tenant_id, last_activity_at DESC NULLS LAST);
    """)
    nordwind = await conn.fetchval(
        "INSERT INTO tenants (slug) VALUES ('nordwind') RETURNING id")
    for slug in ("hansefracht", "baltic"):
        t = await conn.fetchval(
            "INSERT INTO tenants (slug) VALUES ($1) RETURNING id", slug)
        await conn.execute("""
            INSERT INTO tickets (tenant_id, number, requester_email, subject,
                                 last_activity_at)
            SELECT $1, g, 'r@example.com', 'small tenant ticket',
                   now() - g * interval '19 minutes'
            FROM generate_series(1, 5000) g""", t)
    await conn.execute("""
        INSERT INTO agents (tenant_id, email)
        SELECT $1, 'agent' || g || '@nordwind.example'
        FROM generate_series(1, 60) g""", nordwind)
    await conn.execute("""
        INSERT INTO tickets (tenant_id, number, requester_email, subject, status,
                             assignee_id, last_activity_at)
        SELECT $1, g,
               'requester' || (g % 9000) || '@example.com',
               'Ticket #' || g,
               CASE WHEN g % 5 = 0 THEN 'open'
                    WHEN g % 7 = 0 THEN 'pending' ELSE 'solved' END,
               a.id,
               now() - ((g * 13) % 7776000) * interval '1 second'
        FROM generate_series(1, 400000) g
        JOIN (SELECT id, row_number() OVER (ORDER BY id) rn FROM agents) a
          ON a.rn = 1 + (g * 7) % 60""", nordwind)
    # Agent 42 becomes the sparse case: an experienced agent whose queue was
    # cleared on Friday - only 3 open tickets remain, none recently active.
    sparse = await conn.fetchval("""
        SELECT id FROM (SELECT id, row_number() OVER (ORDER BY id) rn
                        FROM agents) a WHERE rn = 42""")
    await conn.execute("""
        UPDATE tickets SET status = 'solved'
        WHERE tenant_id = $1 AND assignee_id = $2 AND status IN ('open','pending')
          AND number NOT IN (SELECT number FROM tickets
                             WHERE tenant_id = $1 AND assignee_id = $2
                               AND status IN ('open','pending')
                             ORDER BY last_activity_at ASC LIMIT 3)""",
        nordwind, sparse)
    await conn.execute("VACUUM ANALYZE tickets")
    busy = await conn.fetchval("""
        SELECT assignee_id FROM tickets
        WHERE tenant_id = $1 AND status IN ('open','pending')
        GROUP BY assignee_id ORDER BY count(*) DESC LIMIT 1""", nordwind)
    print("seeded\n")
    return nordwind, sparse, busy


INBOX = """
    SELECT id, subject, last_activity_at FROM tickets
    WHERE tenant_id = $1 AND assignee_id = $2 AND status IN ('open','pending')
    ORDER BY last_activity_at DESC NULLS LAST LIMIT 50"""


# ---------- A. what an index buys ----------------------------------------------
async def section_a(conn, nordwind) -> None:
    print("A. one ticket out of 410,000, by primary key")
    some_id = await conn.fetchval(
        "SELECT id FROM tickets WHERE tenant_id = $1 AND number = 217113", nordwind)
    await explain(conn, "SELECT subject FROM tickets WHERE id = $1", some_id)
    print("  => root -> inner -> leaf -> heap page: a 410k-row table answered in")
    print("     a handful of 8 KiB page reads. That logarithm is the product (05.5)\n")


# ---------- B. the incident shape and the fix ----------------------------------
async def section_b(conn, nordwind, sparse, busy) -> None:
    print("B. the agent inbox, busy agent vs sparse agent, on the WRONG index")
    print("   -- busy agent (thousands of open tickets):")
    await explain(conn, INBOX, nordwind, busy)
    print("   -- sparse agent (3 open tickets):")
    await explain(conn, INBOX, nordwind, sparse)
    print("   ... the planner walks (tenant, activity) newest-first and FILTERS,")
    print("       so cost = how far it walks before 50 matches. Sparse = the whole")
    print("       tenant. Now the purpose-built index, added the only safe way:")

    t0 = time.perf_counter()
    await conn.execute("""
        CREATE INDEX CONCURRENTLY ix_tickets_inbox
        ON tickets (tenant_id, assignee_id, last_activity_at DESC NULLS LAST)
        WHERE status IN ('open','pending')""")
    build = time.perf_counter() - t0
    full = await conn.fetchval(
        "SELECT pg_relation_size('ix_tickets_tenant_activity')")
    part = await conn.fetchval("SELECT pg_relation_size('ix_tickets_inbox')")
    print(f"   CREATE INDEX CONCURRENTLY: {build:5.2f}s, no write lock held")
    print(f"   sizes: full activity index {full/1024/1024:5.1f} MiB, "
          f"partial inbox index {part/1024/1024:5.1f} MiB (working set only)")
    await conn.execute("ANALYZE tickets")
    print("   -- sparse agent, after:")
    await explain(conn, INBOX, nordwind, sparse)
    print("  => equality columns first (tenant, assignee), the sort column last,")
    print("     the status predicate into the WHERE of a partial index: the query")
    print("     stopped searching and started reading its answer (05.5)\n")


# ---------- C. the leftmost-prefix rule ----------------------------------------
async def section_c(conn, nordwind, busy) -> None:
    print("C. the same composite index, three query shapes")
    print("   -- prefix (tenant, assignee): uses it")
    await explain(conn,
        "SELECT count(*) FROM tickets WHERE tenant_id = $1 AND assignee_id = $2 "
        "AND status = 'open'", nordwind, busy, keys=("Index", "Seq Scan"))
    print("   -- assignee alone (no leading tenant):")
    await explain(conn,
        "SELECT count(*) FROM tickets WHERE assignee_id = $1 AND status = 'open'",
        busy, keys=("Index", "Seq Scan"))
    print("  => a composite index is a phone book sorted by (last, first). Note the")
    print("     'Index Searches' count: PostgreSQL 18's SKIP SCAN rescued the query")
    print("     by probing once per distinct leading value - 3 tenants here. With")
    print("     thousands of tenants that multiplies into thousands of descents:")
    print("     the leading-column rule survives its own exception (05.5)\n")


# ---------- D. index-only scans and the visibility map -------------------------
async def section_d(conn, nordwind) -> None:
    print("D. index-only scans: the visibility map decides the 'only'")
    await conn.execute(
        "UPDATE tickets SET priority = 'high' WHERE tenant_id = $1 "
        "AND number BETWEEN 1 AND 40000", nordwind)
    q = ("SELECT tenant_id, last_activity_at FROM tickets "
         "WHERE tenant_id = $1 ORDER BY last_activity_at DESC NULLS LAST LIMIT 2000")
    print("   -- right after 40k updates:")
    await explain(conn, q, nordwind, keys=("Index Only", "Heap Fetches", "Execution Time"))
    await conn.execute("VACUUM tickets")
    print("   -- after VACUUM:")
    await explain(conn, q, nordwind, keys=("Index Only", "Heap Fetches", "Execution Time"))
    print("  => the index has the columns, but only the visibility map lets the")
    print("     scan skip the heap. Index-only performance is a VACUUM promise,")
    print("     not an index property (05.5, deepened in 05.11)\n")


# ---------- E. what disqualifies an index --------------------------------------
async def section_e(conn, nordwind) -> None:
    print("E. a function on the column hides it from its index")
    await conn.execute(
        "CREATE INDEX ix_tickets_requester ON tickets (tenant_id, requester_email)")
    await conn.execute("ANALYZE tickets")
    print("   -- WHERE lower(requester_email) = ... against the plain index:")
    await explain(conn,
        "SELECT count(*) FROM tickets WHERE tenant_id = $1 "
        "AND lower(requester_email) = 'requester4711@example.com'", nordwind,
        keys=("Index", "Seq Scan", "Filter", "Rows Removed", "Execution Time"))
    await conn.execute("""
        CREATE INDEX ix_tickets_requester_lower
        ON tickets (tenant_id, lower(requester_email))""")
    await conn.execute("ANALYZE tickets")
    print("   -- same query against the expression index:")
    await explain(conn,
        "SELECT count(*) FROM tickets WHERE tenant_id = $1 "
        "AND lower(requester_email) = 'requester4711@example.com'", nordwind,
        keys=("Index", "Seq Scan", "Execution Time"))
    print("  => indexes match EXPRESSIONS, not intentions: lower(col) is a different")
    print("     expression than col. Index the expression you query - or better,")
    print("     normalise at write time (05.3's conventions) (05.5)\n")


# ---------- F. the write bill: HOT updates and WAL -----------------------------
async def section_f(conn, nordwind) -> None:
    print("F. the write bill of one more index (updates on `priority`)")
    async def measure(label: str) -> None:
        await conn.execute("VACUUM tickets")   # reclaim dead tuples: both runs start
        await conn.execute("CHECKPOINT")       # from clean pages, so only the index differs
        w0 = await wal_bytes(conn)
        t0 = time.perf_counter()
        async with conn.transaction():
            await conn.execute(
                "UPDATE tickets SET priority = CASE priority WHEN 'normal' THEN 'low' "
                "ELSE 'normal' END WHERE tenant_id = $1 AND number BETWEEN 100000 AND 120000",
                nordwind)
            # transaction-local stats: this txn's own HOT count, no flush race
            hot = await conn.fetchval(
                "SELECT n_tup_hot_upd FROM pg_stat_xact_user_tables "
                "WHERE relname = 'tickets'")
        elapsed = time.perf_counter() - t0
        wal = (await wal_bytes(conn)) - w0
        print(f"   {label}: 20k updates in {elapsed:4.2f}s, "
              f"wal {wal/1024/1024:6.1f} MiB, HOT updates {hot:,}")

    await measure("priority NOT indexed")
    await conn.execute(
        "CREATE INDEX ix_tickets_priority ON tickets (tenant_id, priority)")
    await measure("priority indexed    ")
    print("  => an update that touches no indexed column can stay HOT (heap-only:")
    print("     no index entries written). Index that column and every update now")
    print("     writes index entries too - the index taxes writes it never serves")
    print("     if nobody queries it (05.5, bloat mechanics in 05.11)\n")


# ---------- G. hygiene ---------------------------------------------------------
async def section_g(conn) -> None:
    print("G. who is actually scanning these indexes?")
    rows = await conn.fetch("""
        SELECT s.indexrelname, s.idx_scan, i.indisunique,
               pg_size_pretty(pg_relation_size(s.indexrelid)) AS size
        FROM pg_stat_user_indexes s JOIN pg_index i ON i.indexrelid = s.indexrelid
        WHERE s.relname = 'tickets'
        ORDER BY s.idx_scan, s.indexrelname""")
    for r in rows:
        if r["idx_scan"] == 0 and not r["indisunique"]:
            flag = "   <- cost, no benefit: drop candidate"
        elif r["idx_scan"] == 0:
            flag = "   (unique: serves integrity, not queries - keep)"
        else:
            flag = ""
        print(f"   {r['indexrelname']:34s} scans={r['idx_scan']:>4}  "
              f"size={r['size']}{flag}")
    print("  => pg_stat_user_indexes is the audit: an unscanned NON-unique index is")
    print("     pure write amplification - DROP INDEX CONCURRENTLY it. Unique ones")
    print("     may be doing constraint work at zero scans; check before dropping (05.5)")


async def main() -> None:
    conn = await asyncpg.connect(DSN)
    try:
        nordwind, sparse, busy = await seed(conn)
        await section_a(conn, nordwind)
        await section_b(conn, nordwind, sparse, busy)
        await section_c(conn, nordwind, busy)
        await section_d(conn, nordwind)
        await section_e(conn, nordwind)
        await section_f(conn, nordwind)
        await section_g(conn)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
