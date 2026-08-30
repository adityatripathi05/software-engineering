"""Lab for 05.3 Constraints, data integrity and upsert.

Reproduces the notebook's captures against the module compose.yaml (PostgreSQL 18):
  A. an unconstrained status column accepting garbage; the named CHECK refusing
     it with the constraint name in the error (03.8's mapping key)
  B. adding a CHECK to a live table: plain ADD failing on existing garbage,
     NOT VALID protecting new writes instantly, repair, then VALIDATE - timed
  C. evolving a closed vocabulary: CHECK vs ENUM type vs lookup table
  D. upsert: the SELECT-then-INSERT race vs ON CONFLICT (measured with 20
     concurrent writers), the DO NOTHING + RETURNING trap, and identity burn
  E. the gapless per-tenant allocator: naive max+1 duplicating under
     concurrency, the counter-row upsert allocating 1..N exactly, a rollback
     REUSING its number, and the per-tenant serialisation cost measured
  F. conventions: timestamp vs timestamptz (one row, two instants), float money

Run:  docker compose up -d --wait   (in the module directory), then
      python lab_05_03_constraints.py
"""
import asyncio
import sys
import time

import asyncpg

if sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DSN = "postgresql://deskhub:deskhub_dev@127.0.0.1:55432/deskhub"


# ---------- seed ---------------------------------------------------------------
async def seed(conn: asyncpg.Connection) -> str:
    print("seeding: tenants + 200,000 tickets, 500 of them with garbage statuses ...")
    await conn.execute("""
        DROP TABLE IF EXISTS attachments, comments, tickets, agents, tenants,
                             ticket_counters CASCADE;
        CREATE TABLE tenants (
            id   uuid PRIMARY KEY DEFAULT uuidv7(),
            slug text NOT NULL UNIQUE,
            name text NOT NULL
        );
        CREATE TABLE tickets (
            id         uuid PRIMARY KEY DEFAULT uuidv7(),
            tenant_id  uuid NOT NULL REFERENCES tenants(id),
            number     bigint NOT NULL,
            subject    text NOT NULL,
            status     text NOT NULL DEFAULT 'open',     -- unconstrained: the launch state
            created_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, number)
        );
    """)
    tenant = await conn.fetchval(
        "INSERT INTO tenants (slug, name) VALUES ('nordwind', 'Nordwind Logistik GmbH') "
        "RETURNING id")
    await conn.execute("""
        INSERT INTO tickets (tenant_id, number, subject, status)
        SELECT $1, g, 'Ticket #' || g,
               CASE
                   WHEN g % 400 = 0 THEN 'Solved'        -- the ERP's capitalised state
                   WHEN g % 401 = 0 THEN 'open '         -- trailing space
                   WHEN g % 4 = 0 THEN 'solved'
                   ELSE 'open'
               END
        FROM generate_series(1, 200000) g""", tenant)
    n = await conn.fetchval(
        "SELECT count(*) FROM tickets WHERE status NOT IN ('open','pending','solved','closed')")
    print(f"seeded: 200,000 tickets, {n} with statuses outside the vocabulary\n")
    return tenant


# ---------- A. the last validator ----------------------------------------------
async def section_a(conn: asyncpg.Connection, tenant: str) -> None:
    print("A. who validates? every write path, or the one validator they all share")
    for i, bad in enumerate(("Solved", "open ", "")):
        await conn.execute(
            "INSERT INTO tickets (tenant_id, number, subject, status) "
            "VALUES ($1, 900000 + $2, 'probe', $3)", tenant, i, bad)
        print(f"   unconstrained column: INSERT status={bad!r:10s} -> accepted")
    await conn.execute(
        "DELETE FROM tickets WHERE number >= 900000")
    print("   ... add the named CHECK (section B), then the same inserts:")


async def section_a2(conn: asyncpg.Connection, tenant: str) -> None:
    for bad in ("Solved", "open ", ""):
        try:
            await conn.execute(
                "INSERT INTO tickets (tenant_id, number, subject, status) "
                "VALUES ($1, 900000, 'probe', $2)", tenant, bad)
        except asyncpg.CheckViolationError as exc:
            print(f"   constrained column:  INSERT status={bad!r:10s} -> "
                  f"CheckViolationError, constraint_name={exc.constraint_name!r}")
    print("  => the error carries the CONSTRAINT NAME - the stable key 03.8's")
    print("     repository mapping turns into a catalogue problem (05.3)\n")


# ---------- B. constraining a live table ---------------------------------------
async def section_b(conn: asyncpg.Connection) -> None:
    print("B. adding the CHECK to a live 200k-row table")
    t0 = time.perf_counter()
    try:
        await conn.execute("""
            ALTER TABLE tickets ADD CONSTRAINT ck_tickets_status
                CHECK (status IN ('open','pending','solved','closed'))""")
    except asyncpg.CheckViolationError as exc:
        print(f"   plain ADD CONSTRAINT   -> FAILS after {time.perf_counter()-t0:5.2f}s "
              f"scanning: {exc.message.splitlines()[0]}")
    t0 = time.perf_counter()
    await conn.execute("""
        ALTER TABLE tickets ADD CONSTRAINT ck_tickets_status
            CHECK (status IN ('open','pending','solved','closed')) NOT VALID""")
    print(f"   ADD ... NOT VALID      -> ok in {(time.perf_counter()-t0)*1000:5.1f} ms "
          "(no scan; NEW writes constrained from this instant)")
    repaired = await conn.execute("""
        UPDATE tickets SET status = CASE
            WHEN lower(trim(status)) IN ('open','pending','solved','closed')
                THEN lower(trim(status))
            ELSE 'open' END
        WHERE status NOT IN ('open','pending','solved','closed')""")
    print(f"   repair the stock       -> {repaired}")
    t0 = time.perf_counter()
    await conn.execute("ALTER TABLE tickets VALIDATE CONSTRAINT ck_tickets_status")
    print(f"   VALIDATE CONSTRAINT    -> ok in {time.perf_counter()-t0:5.2f}s "
          "(scans, but under a weaker lock: writes continue)")
    print("  => the two-step is the zero-downtime path: protect the door first,")
    print("     clean the room second, then certify it (05.3)\n")


# ---------- C. evolving a closed vocabulary ------------------------------------
async def section_c(conn: asyncpg.Connection) -> None:
    print("C. the vocabulary needs a new value ('on_hold') - three mechanisms")
    t0 = time.perf_counter()
    await conn.execute("""
        ALTER TABLE tickets DROP CONSTRAINT ck_tickets_status;
        ALTER TABLE tickets ADD CONSTRAINT ck_tickets_status
            CHECK (status IN ('open','pending','on_hold','solved','closed')) NOT VALID;
        ALTER TABLE tickets VALIDATE CONSTRAINT ck_tickets_status;
    """)
    print(f"   CHECK:  drop + re-add + validate    -> {time.perf_counter()-t0:5.2f}s, "
          "plain DDL, reversible")

    await conn.execute("""
        DROP TYPE IF EXISTS ticket_status;
        CREATE TYPE ticket_status AS ENUM ('open','pending','solved','closed');
    """)
    await conn.execute("ALTER TYPE ticket_status ADD VALUE 'on_hold' BEFORE 'solved'")
    print("   ENUM:   ALTER TYPE ADD VALUE        -> ok (cheap to add ...)")
    try:
        await conn.execute("ALTER TYPE ticket_status DROP VALUE 'on_hold'")
    except asyncpg.PostgresError as exc:
        print(f"   ENUM:   ALTER TYPE DROP VALUE       -> {exc.message.splitlines()[0]}")

    await conn.execute("""
        DROP TABLE IF EXISTS statuses CASCADE;
        CREATE TABLE statuses (code text PRIMARY KEY);
        INSERT INTO statuses VALUES ('open'),('pending'),('solved'),('closed');
        INSERT INTO statuses VALUES ('on_hold');
    """)
    print("   LOOKUP: INSERT INTO statuses        -> a data change, not DDL "
          "(and the FK can carry ON DELETE semantics)")
    print("  => adding is easy everywhere; REMOVING is where they differ - and")
    print("     enum values can never be dropped (05.3)\n")


# ---------- D. upsert ----------------------------------------------------------
async def section_d(pool: asyncpg.Pool, tenant: str) -> None:
    print("D. idempotent ingestion: SELECT-then-INSERT vs ON CONFLICT")
    async with pool.acquire() as conn:
        await conn.execute("""
            DROP TABLE IF EXISTS erp_tickets;
            CREATE TABLE erp_tickets (
                id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                external_ref text NOT NULL,
                subject      text NOT NULL,
                CONSTRAINT uq_erp_tickets_external_ref UNIQUE (external_ref)
            );
        """)

    async def check_then_act(ref: str) -> str:
        async with pool.acquire() as conn:
            exists = await conn.fetchval(
                "SELECT 1 FROM erp_tickets WHERE external_ref = $1", ref)
            await asyncio.sleep(0.02)                # the window every real handler has
            if exists:
                return "skipped"
            try:
                await conn.execute(
                    "INSERT INTO erp_tickets (external_ref, subject) VALUES ($1, 'sync')",
                    ref)
                return "inserted"
            except asyncpg.UniqueViolationError:
                return "unique_violation"

    outcomes = await asyncio.gather(*[check_then_act("SO-88213") for _ in range(20)])
    counts = {o: outcomes.count(o) for o in set(outcomes)}
    print(f"   20 concurrent check-then-act, same ref : {counts}")

    async def upsert(ref: str) -> str:
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO erp_tickets (external_ref, subject) VALUES ($1, 'sync v2')
                ON CONFLICT ON CONSTRAINT uq_erp_tickets_external_ref
                DO UPDATE SET subject = excluded.subject
                RETURNING id""", ref)
            return f"row {row['id']}"

    outcomes = await asyncio.gather(*[upsert("SO-99417") for _ in range(20)])
    rows = await pool.fetchval(
        "SELECT count(*) FROM erp_tickets WHERE external_ref = 'SO-99417'")
    print(f"   20 concurrent ON CONFLICT DO UPDATE   : all -> {set(outcomes)}, "
          f"{rows} row in the table")

    got = await pool.fetchrow("""
        INSERT INTO erp_tickets (external_ref, subject) VALUES ('SO-99417', 'x')
        ON CONFLICT (external_ref) DO NOTHING RETURNING id""")
    print(f"   DO NOTHING ... RETURNING on a conflict : returned {got!r}   "
          "<- no row, no error")
    next_id = await pool.fetchval(
        "INSERT INTO erp_tickets (external_ref, subject) VALUES ('SO-00001', 'fresh') "
        "RETURNING id")
    print(f"   next fresh insert's identity           : id={next_id}  "
          "<- every conflicting attempt burned a number")
    print("  => the constraint is the check and the act, in one statement; but")
    print("     DO NOTHING returns nothing, and identity gaps grow per conflict (05.3)\n")


# ---------- E. the gapless per-tenant allocator --------------------------------
async def section_e(pool: asyncpg.Pool, tenant: str) -> None:
    print("E. per-tenant ticket numbers: naive max+1 vs the counter row")
    async with pool.acquire() as conn:
        await conn.execute("""
            DROP TABLE IF EXISTS numbered;
            CREATE TABLE numbered (tenant_id uuid, n bigint, note text);
            CREATE TABLE IF NOT EXISTS ticket_counters (
                tenant_id   uuid PRIMARY KEY REFERENCES tenants(id),
                last_number bigint NOT NULL DEFAULT 0
            );
        """)

    async def naive(tenant_id: str) -> None:
        async with pool.acquire() as conn:
            n = await conn.fetchval(
                "SELECT coalesce(max(n), 0) + 1 FROM numbered WHERE tenant_id = $1",
                tenant_id)
            await asyncio.sleep(0.02)
            await conn.execute(
                "INSERT INTO numbered (tenant_id, n, note) VALUES ($1, $2, 'naive')",
                tenant_id, n)

    await asyncio.gather(*[naive(tenant) for _ in range(20)])
    row = await pool.fetchrow(
        "SELECT count(*) AS rows, count(DISTINCT n) AS distinct_n FROM numbered")
    print(f"   naive max+1, 20 concurrent            : {row['rows']} rows but only "
          f"{row['distinct_n']} distinct numbers")

    ALLOCATE = """
        INSERT INTO ticket_counters AS c (tenant_id, last_number) VALUES ($1, 1)
        ON CONFLICT (tenant_id) DO UPDATE SET last_number = c.last_number + 1
        RETURNING last_number"""

    async def allocate_and_insert(tenant_id: str) -> None:
        async with pool.acquire() as conn, conn.transaction():
            n = await conn.fetchval(ALLOCATE, tenant_id)
            await asyncio.sleep(0.002)               # building the ticket row etc.
            await conn.execute(
                "INSERT INTO numbered (tenant_id, n, note) VALUES ($1, $2, 'counter')",
                tenant_id, n)

    await pool.execute("TRUNCATE numbered")
    await asyncio.gather(*[allocate_and_insert(tenant) for _ in range(20)])
    row = await pool.fetchrow("""
        SELECT count(*) AS rows, count(DISTINCT n) AS distinct_n, min(n) AS lo, max(n) AS hi
        FROM numbered""")
    print(f"   counter-row allocator, 20 concurrent  : {row['rows']} rows, "
          f"{row['distinct_n']} distinct, numbers {row['lo']}..{row['hi']}")

    async with pool.acquire() as conn:
        tx = conn.transaction()
        await tx.start()
        doomed = await conn.fetchval(ALLOCATE, tenant)
        await tx.rollback()
        reused = await conn.fetchval(ALLOCATE, tenant)
        await conn.execute(
            "INSERT INTO numbered (tenant_id, n, note) VALUES ($1, $2, 'after-rollback')",
            tenant, reused)
    print(f"   allocate {doomed} then ROLLBACK -> next allocation gets {reused}   "
          "<- gapless, because the bump dies with the txn")

    async with pool.acquire() as conn:
        slugs = [f"t{i}" for i in range(10)]
        others = [await conn.fetchval(
            "INSERT INTO tenants (slug, name) VALUES ($1, $1) RETURNING id", s)
            for s in slugs]
    t0 = time.perf_counter()
    await asyncio.gather(*[allocate_and_insert(tenant) for _ in range(300)])
    hot = time.perf_counter() - t0
    t0 = time.perf_counter()
    await asyncio.gather(*[allocate_and_insert(others[i % 10]) for i in range(300)])
    spread = time.perf_counter() - t0
    print(f"   300 allocations, ONE tenant           : {hot:5.2f}s   "
          "<- serialised on one counter row")
    print(f"   300 allocations, TEN tenants          : {spread:5.2f}s")
    print("  => gapless = the bump rides the ticket's transaction, so the row lock")
    print("     is held to commit: creation serialises PER TENANT. That is the")
    print("     price of gaplessness - sequences gap precisely to avoid it (05.3)\n")


# ---------- F. conventions: time and money -------------------------------------
async def section_f(conn: asyncpg.Connection) -> None:
    print("F. column conventions: timestamptz vs timestamp, numeric vs float")
    await conn.execute("""
        DROP TABLE IF EXISTS conv;
        CREATE TABLE conv (with_tz timestamptz, naive timestamp);
        SET TIME ZONE 'Europe/Berlin';
        INSERT INTO conv VALUES (now(), now());
    """)
    for zone in ("Europe/Berlin", "UTC"):
        await conn.execute(f"SET TIME ZONE '{zone}'")
        row = await conn.fetchrow(
            "SELECT with_tz::text AS tz_text, naive::text AS naive_text, "
            "       (with_tz = naive) AS same_instant FROM conv")
        print(f"   read in {zone:13s}: timestamptz={row['tz_text']}   "
              f"timestamp={row['naive_text']}   same instant? {row['same_instant']}")
    await conn.execute("SET TIME ZONE 'UTC'")
    print("     -> the timestamptz is one instant, rendered per reader; the naive")
    print("        column is bare digits whose MEANING moves with the session zone")

    row = await conn.fetchrow("""
        SELECT (0.10::float8 * 3)                    AS f_sum,
               (0.10::float8 * 3 = 0.30::float8)     AS f_eq,
               (0.10::numeric * 3)                   AS n_sum""")
    print(f"   0.10 * 3 as float8  = {row['f_sum']!r}  (equals 0.30? {row['f_eq']})")
    print(f"   0.10 * 3 as numeric = {row['n_sum']}")
    print("  => timestamptz always; numeric (or bigint minor units) for money -")
    print("     03.4's rule, now enforced where every path meets it (05.3)")


async def main() -> None:
    pool = await asyncpg.create_pool(DSN, min_size=10, max_size=10)
    try:
        async with pool.acquire() as conn:
            tenant = await seed(conn)
            await section_a(conn, tenant)
            await section_b(conn)
            await section_a2(conn, tenant)
            await section_c(conn)
        await section_d(pool, tenant)
        await section_e(pool, tenant)
        async with pool.acquire() as conn:
            await section_f(conn)
    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
