"""Lab for 05.1 Relational modelling and key choice - serial, UUIDv4, UUIDv7.

Reproduces the notebook's captures against the module compose.yaml (PostgreSQL 18):
  A. what each key generator actually produces: insertion order vs sort order,
     and the timestamp embedded in a UUIDv7 (uuid_extract_timestamp)
  B. identity/serial gaps: a rolled-back insert consumes the sequence value
  C. index geometry after 1M ordered vs random keys: build time, WAL bytes,
     primary-key index size, avg_leaf_density / leaf_fragmentation (pgstattuple)
  D. steady-state WAL amplification: CHECKPOINT, then 100k more inserts per
     table - random keys touch (and full-page-image) nearly every leaf page
  E. what ORDER BY id DESC means per key type: the newest-100 window, plus the
     backward index scan's EXPLAIN(ANALYZE, BUFFERS)
  F. the founding Deskhub schema (tenants/agents/tickets/comments/attachments)
     created and exercised end to end

Run:  docker compose up -d --wait   (in the module directory), then
      python lab_05_01_keys.py
"""
import asyncio
import sys
import time

import asyncpg

# Windows: a redirected stdout falls back to cp1252; force UTF-8 so captures
# with arrows/box characters never kill the run (04.8's lab lesson).
if sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DSN = "postgresql://deskhub:deskhub_dev@127.0.0.1:55432/deskhub"

ROWS_INITIAL = 1_000_000
ROWS_STEADY = 100_000

TABLES = {
    "k_identity": "id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY",
    "k_uuidv4": "id uuid DEFAULT gen_random_uuid() PRIMARY KEY",
    "k_uuidv7": "id uuid DEFAULT uuidv7() PRIMARY KEY",
}


async def wal_bytes(conn: asyncpg.Connection) -> int:
    return await conn.fetchval(
        "SELECT pg_wal_lsn_diff(pg_current_wal_insert_lsn(), '0/0')::bigint")


def mib(n: int) -> str:
    return f"{n / 1024 / 1024:7.1f} MiB"


# ---------- A. what the generators produce ------------------------------------
async def section_a(conn: asyncpg.Connection) -> None:
    print("A. five rows inserted 5ms apart - does the KEY remember the order?")
    await conn.execute("""
        DROP TABLE IF EXISTS arrival;
        CREATE TABLE arrival (arrived int, v4 uuid, v7 uuid);
    """)
    for i in range(1, 6):
        await conn.execute(
            "INSERT INTO arrival VALUES ($1, gen_random_uuid(), uuidv7())", i)
        await asyncio.sleep(0.005)                    # tick the ms clock between rows

    by_v4 = [r["arrived"] for r in await conn.fetch("SELECT arrived FROM arrival ORDER BY v4")]
    by_v7 = [r["arrived"] for r in await conn.fetch("SELECT arrived FROM arrival ORDER BY v7")]
    print(f"   arrival order      : [1, 2, 3, 4, 5]")
    print(f"   ORDER BY v4 gives  : {by_v4}   <- random bits sort in random order")
    print(f"   ORDER BY v7 gives  : {by_v7}   <- the timestamp prefix sorts by time")

    row = await conn.fetchrow("""
        SELECT v7, uuid_extract_timestamp(v7) AS embedded,
               now() AS db_now
        FROM arrival WHERE arrived = 5""")
    print(f"   a v7 key           : {row['v7']}")
    print(f"   its embedded time  : {row['embedded']}  (uuid_extract_timestamp)")
    print(f"   db clock right now : {row['db_now']}")
    print("  => a UUIDv7 carries its own creation instant in the first 48 bits;")
    print("     a UUIDv4 carries nothing but noise (05.1)\n")


# ---------- B. identity gaps ---------------------------------------------------
async def section_b(conn: asyncpg.Connection) -> None:
    print("B. identity columns and gaps: a rollback consumes the number anyway")
    await conn.execute("""
        DROP TABLE IF EXISTS gap_demo;
        CREATE TABLE gap_demo (
            id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            note text NOT NULL
        );
    """)
    await conn.execute("INSERT INTO gap_demo (note) VALUES ('first')")
    tx = conn.transaction()
    await tx.start()
    await conn.execute("INSERT INTO gap_demo (note) VALUES ('doomed')")
    await tx.rollback()                               # the row dies; nextval does not rewind
    await conn.execute("INSERT INTO gap_demo (note) VALUES ('third')")
    rows = await conn.fetch("SELECT id, note FROM gap_demo ORDER BY id")
    for r in rows:
        print(f"   id={r['id']}  note={r['note']}")
    print("  => sequences never rewind: gaps are normal operation, not data loss.")
    print("     Anything requiring gapless numbers (invoice/ticket numbers) is a")
    print("     separate, transactional allocation - 05.3 builds it (05.1)\n")


# ---------- C. index geometry after 1M inserts ---------------------------------
async def section_c(conn: asyncpg.Connection) -> None:
    print(f"C. {ROWS_INITIAL:,} inserts per key type - what did the B-tree become?")
    await conn.execute("CREATE EXTENSION IF NOT EXISTS pgstattuple")
    results = {}
    for table, key_ddl in TABLES.items():
        await conn.execute(f"""
            DROP TABLE IF EXISTS {table};
            CREATE TABLE {table} (
                {key_ddl},
                created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
                pad text NOT NULL
            );
        """)
        await conn.execute("CHECKPOINT")
        wal0 = await wal_bytes(conn)
        t0 = time.perf_counter()
        await conn.execute(f"""
            INSERT INTO {table} (pad)
            SELECT 'ticket payload placeholder' FROM generate_series(1, {ROWS_INITIAL})
        """)
        elapsed = time.perf_counter() - t0
        wal = await wal_bytes(conn) - wal0
        size = await conn.fetchval(
            "SELECT pg_relation_size(indexrelid) FROM pg_stat_user_indexes "
            "WHERE relname = $1", table)
        stat = await conn.fetchrow(
            f"SELECT avg_leaf_density, leaf_fragmentation "
            f"FROM pgstatindex('{table}_pkey')")
        results[table] = (elapsed, wal, size, stat)
        print(f"   {table:11s}  insert {elapsed:5.1f}s   wal {mib(wal)}   "
              f"pkey {mib(size)}   leaf_density {stat['avg_leaf_density']:5.1f}%   "
              f"fragmentation {stat['leaf_fragmentation']:5.1f}%")
    print("  => ordered keys append at the rightmost leaf (90/10 split: pages left")
    print("     ~90% full); random keys split everywhere (50/50: pages left ~50-70%")
    print("     full) - same rows, same column type, a fatter and shuffled index (05.1)\n")


# ---------- D. steady-state WAL amplification ----------------------------------
async def section_d(conn: asyncpg.Connection) -> None:
    print(f"D. CHECKPOINT, then {ROWS_STEADY:,} MORE inserts - the steady-state bill")
    for table in TABLES:
        await conn.execute("CHECKPOINT")              # reset full-page-image debts
        wal0 = await wal_bytes(conn)
        t0 = time.perf_counter()
        await conn.execute(f"""
            INSERT INTO {table} (pad)
            SELECT 'ticket payload placeholder' FROM generate_series(1, {ROWS_STEADY})
        """)
        elapsed = time.perf_counter() - t0
        wal = await wal_bytes(conn) - wal0
        print(f"   {table:11s}  insert {elapsed:5.1f}s   wal {mib(wal)}")
    print("  => after a checkpoint, the FIRST touch of each 8 KiB page writes a")
    print("     full-page image to WAL. Ordered keys touch a handful of rightmost")
    print("     leaves; random keys touch nearly EVERY leaf - the same rows cost")
    print("     ~3x the WAL here, and the multiplier GROWS with index size (05.1)\n")


# ---------- E. what ORDER BY id means ------------------------------------------
async def section_e(conn: asyncpg.Connection) -> None:
    print('E. "the 100 newest tickets": ORDER BY id DESC LIMIT 100, per key type')
    for table in TABLES:
        row = await conn.fetchrow(f"""
            WITH newest AS (SELECT created_at FROM {table} ORDER BY id DESC LIMIT 100)
            SELECT now() - min(created_at) AS oldest_in_page,
                   now() - max(created_at) AS newest_in_page
            FROM newest""")
        print(f"   {table:11s}  page spans rows created between "
              f"{row['oldest_in_page'].total_seconds():7.1f}s and "
              f"{row['newest_in_page'].total_seconds():5.1f}s ago")
    plan = await conn.fetch(
        "EXPLAIN (ANALYZE, BUFFERS) SELECT id FROM k_uuidv7 ORDER BY id DESC LIMIT 100")
    for line in plan[:4]:
        print(f"     {line[0]}")
    print("  => the scan itself is cheap on every key type - but only identity and")
    print("     v7 mean 'newest' by id. Under v4, ORDER BY id is a random sample")
    print("     wearing a deterministic face (05.1)\n")


# ---------- F. the founding Deskhub schema -------------------------------------
SCHEMA = """
DROP TABLE IF EXISTS attachments, comments, tickets, agents, tenants CASCADE;

CREATE TABLE tenants (
    id          uuid PRIMARY KEY DEFAULT uuidv7(),
    slug        text NOT NULL UNIQUE,
    name        text NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE agents (
    id           uuid PRIMARY KEY DEFAULT uuidv7(),
    tenant_id    uuid NOT NULL REFERENCES tenants(id),
    email        text NOT NULL,
    display_name text NOT NULL,
    created_at   timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, email)
);

CREATE TABLE tickets (
    id              uuid PRIMARY KEY DEFAULT uuidv7(),
    tenant_id       uuid NOT NULL REFERENCES tenants(id),
    number          bigint NOT NULL,
    requester_email text NOT NULL,
    subject         text NOT NULL,
    status          text NOT NULL DEFAULT 'open',
    priority        text NOT NULL DEFAULT 'normal',
    assignee_id     uuid REFERENCES agents(id),
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, number)
);

CREATE TABLE comments (
    id              uuid PRIMARY KEY DEFAULT uuidv7(),
    ticket_id       uuid NOT NULL REFERENCES tickets(id),
    author_agent_id uuid REFERENCES agents(id),
    body            text NOT NULL,
    is_internal     boolean NOT NULL DEFAULT false,
    created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE attachments (
    id           uuid PRIMARY KEY DEFAULT uuidv7(),
    comment_id   uuid NOT NULL REFERENCES comments(id),
    filename     text NOT NULL,
    content_type text NOT NULL,
    byte_size    bigint NOT NULL,
    storage_key  text NOT NULL,
    created_at   timestamptz NOT NULL DEFAULT now()
);
"""


async def section_f(conn: asyncpg.Connection) -> None:
    print("F. the founding Deskhub schema, created and exercised")
    await conn.execute(SCHEMA)
    tenant = await conn.fetchval(
        "INSERT INTO tenants (slug, name) VALUES ('nordwind', 'Nordwind Logistik GmbH') "
        "RETURNING id")
    agent = await conn.fetchval(
        "INSERT INTO agents (tenant_id, email, display_name) "
        "VALUES ($1, 'anna@nordwind.example', 'Anna Weber') RETURNING id", tenant)
    ticket = await conn.fetchval(
        "INSERT INTO tickets (tenant_id, number, requester_email, subject, assignee_id) "
        "VALUES ($1, 1, 'kunde@example.com', 'Cannot download invoice PDF', $2) "
        "RETURNING id", tenant, agent)
    comment = await conn.fetchval(
        "INSERT INTO comments (ticket_id, author_agent_id, body) "
        "VALUES ($1, $2, 'Reproduced - the export link is expired.') RETURNING id",
        ticket, agent)
    await conn.execute(
        "INSERT INTO attachments (comment_id, filename, content_type, byte_size, storage_key) "
        "VALUES ($1, 'screenshot.png', 'image/png', 48211, 'att/2026/12/screenshot.png')",
        comment)
    row = await conn.fetchrow("""
        SELECT t.id, t.subject, uuid_extract_timestamp(t.id) AS keyed_at,
               (SELECT count(*) FROM comments c WHERE c.ticket_id = t.id) AS comments,
               a.display_name AS assignee
        FROM tickets t JOIN agents a ON a.id = t.assignee_id
        WHERE t.tenant_id = $1 AND t.number = 1""", tenant)
    print(f"   ticket id   : {row['id']}")
    print(f"   keyed_at    : {row['keyed_at']}   (the id itself says when)")
    print(f"   subject     : {row['subject']!r}  assignee={row['assignee']!r}  "
          f"comments={row['comments']}")
    print("  => five tables, every relationship a foreign key pointing child->parent,")
    print("     every natural identity (slug, tenant+email, tenant+number) a UNIQUE")
    print("     constraint under a surrogate v7 primary key (05.1)")


async def main() -> None:
    conn = await asyncpg.connect(DSN)
    try:
        await section_a(conn)
        await section_b(conn)
        await section_c(conn)
        await section_d(conn)
        await section_e(conn)
        await section_f(conn)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
