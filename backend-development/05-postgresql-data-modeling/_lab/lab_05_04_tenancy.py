"""Lab for 05.4 Multi-tenant data modelling.

Reproduces the notebook's captures against the module compose.yaml (PostgreSQL 18):
  A. the cross-tenant WRITE the launch schema cannot refuse: a ticket-merge
     UPDATE moves one tenant's comments onto another tenant's ticket, silently -
     and the join-based audit query that finds the contamination
  B. making it unrepresentable: tenant_id denormalised onto comments (backfill,
     05.3's NOT VALID -> VALIDATE discipline) + the composite FK - the same
     hostile UPDATE now fails, naming the constraint
  C. row-level security as the read floor: the owner-bypass gotcha (policies
     ignored until FORCE), scoping without any WHERE clause, fail-closed when
     the GUC is unset, and WITH CHECK refusing wrong-tenant writes
  D. the GUC is connection state: a session-level SET bleeding across two
     logical requests on one connection (PgBouncer's world), SET LOCAL dying
     with its transaction, and asyncpg's pool reset wiping session state
  E. the planner's view: the RLS qual folded into the inbox query's index scan

Run:  docker compose up -d --wait   (in the module directory), then
      python lab_05_04_tenancy.py
"""
import asyncio
import sys

import asyncpg

if sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DSN = "postgresql://deskhub:deskhub_dev@127.0.0.1:55432/deskhub"

TENANTS = {"nordwind": "Nordwind Logistik GmbH",
           "hansefracht": "HanseFracht AG",
           "baltic": "Baltic Freight Startup"}


# ---------- seed: canon schema as of 05.3 (comments have NO tenant_id yet) -----
SCHEMA = """
DROP TABLE IF EXISTS attachments, comments, tickets, agents, tenants,
                     ticket_counters CASCADE;
CREATE TABLE tenants (
    id   uuid PRIMARY KEY DEFAULT uuidv7(),
    slug text NOT NULL UNIQUE,
    name text NOT NULL
);
CREATE TABLE agents (
    id        uuid PRIMARY KEY DEFAULT uuidv7(),
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    email     text NOT NULL,
    UNIQUE (tenant_id, email)
);
CREATE TABLE tickets (
    id         uuid PRIMARY KEY DEFAULT uuidv7(),
    tenant_id  uuid NOT NULL REFERENCES tenants(id),
    number     bigint NOT NULL,
    subject    text NOT NULL,
    status     text NOT NULL DEFAULT 'open'
        CONSTRAINT ck_tickets_status CHECK (status IN ('open','pending','solved','closed')),
    last_activity_at timestamptz,
    UNIQUE (tenant_id, number)
);
CREATE INDEX ix_tickets_tenant_activity
    ON tickets (tenant_id, last_activity_at DESC NULLS LAST);
CREATE TABLE comments (
    id              uuid PRIMARY KEY DEFAULT uuidv7(),
    ticket_id       uuid NOT NULL REFERENCES tickets(id),   -- launch shape: tenant-blind
    author_agent_id uuid REFERENCES agents(id),
    body            text NOT NULL,
    is_internal     boolean NOT NULL DEFAULT false
);
CREATE INDEX ix_comments_ticket ON comments (ticket_id);
"""


async def seed(conn: asyncpg.Connection) -> dict[str, str]:
    print("seeding: 3 tenants x 5,000 tickets, ~10,000 comments each ...")
    await conn.execute(SCHEMA)
    ids: dict[str, str] = {}
    for slug, name in TENANTS.items():
        tenant = await conn.fetchval(
            "INSERT INTO tenants (slug, name) VALUES ($1, $2) RETURNING id", slug, name)
        ids[slug] = tenant
        agent = await conn.fetchval(
            "INSERT INTO agents (tenant_id, email) VALUES ($1, $2) RETURNING id",
            tenant, f"agent@{slug}.example")
        await conn.execute("""
            INSERT INTO tickets (tenant_id, number, subject, last_activity_at)
            SELECT $1, g, $2 || ' ticket #' || g, now() - g * interval '7 minutes'
            FROM generate_series(1, 5000) g""", tenant, slug)
        await conn.execute("""
            INSERT INTO comments (ticket_id, author_agent_id, body, is_internal)
            SELECT t.id, $2, 'reply ' || g, g = 2
            FROM tickets t, generate_series(1, 2) g WHERE t.tenant_id = $1""",
            tenant, agent)
    await conn.execute("ANALYZE")
    print("seeded\n")
    return ids


AUDIT = """
    SELECT count(*) FROM comments c
    JOIN tickets t ON t.id = c.ticket_id
    JOIN agents a  ON a.id = c.author_agent_id
    WHERE a.tenant_id <> t.tenant_id"""


# ---------- A. the write the schema cannot refuse ------------------------------
async def section_a(conn: asyncpg.Connection, ids: dict[str, str]) -> None:
    print("A. the merge tool's UPDATE, with a wrong source id from another tenant")
    src = await conn.fetchval(
        "SELECT id FROM tickets WHERE tenant_id = $1 AND number = 212", ids["nordwind"])
    dst = await conn.fetchval(
        "SELECT id FROM tickets WHERE tenant_id = $1 AND number = 212", ids["baltic"])
    await conn.execute(
        "UPDATE comments SET body = 'internal: Nordwind renewal - propose 8% uplift' "
        "WHERE ticket_id = $1 AND is_internal", src)
    moved = await conn.execute(
        "UPDATE comments SET ticket_id = $1 WHERE ticket_id = $2", dst, src)
    print(f"   move Nordwind #212's comments onto Baltic #212 : {moved}   <- no error")
    leaked = await conn.fetch("""
        SELECT c.body, c.is_internal FROM comments c
        JOIN tickets t ON t.id = c.ticket_id
        WHERE t.tenant_id = $1 AND t.number = 212 ORDER BY c.is_internal, c.body""",
        ids["baltic"])
    for r in leaked:
        tag = "INTERNAL NOTE" if r["is_internal"] else "public reply"
        print(f"     Baltic's ticket #212 now shows: {r['body']!r}  ({tag})")
    print(f"   author-vs-ticket tenant audit finds            : "
          f"{await conn.fetchval(AUDIT)} contaminated comments")
    print("  => the FK checked 'is this a ticket?', never 'is this OUR ticket?'.")
    print("     A cross-tenant reference is representable, so someday it is real (05.4)\n")


# ---------- B. make it unrepresentable -----------------------------------------
async def section_b(conn: asyncpg.Connection, ids: dict[str, str]) -> None:
    print("B. repair, then tenant_id onto comments + the composite foreign key")
    src = await conn.fetchval(
        "SELECT id FROM tickets WHERE tenant_id = $1 AND number = 212", ids["nordwind"])
    dst = await conn.fetchval(
        "SELECT id FROM tickets WHERE tenant_id = $1 AND number = 212", ids["baltic"])
    await conn.execute("""
        UPDATE comments c SET ticket_id = $1
        FROM agents a WHERE a.id = c.author_agent_id
          AND c.ticket_id = $2 AND a.tenant_id <> (SELECT tenant_id FROM tickets
                                                   WHERE id = $2)""", src, dst)
    print(f"   repair (audit-guided move back)         : audit now finds "
          f"{await conn.fetchval(AUDIT)}")
    await conn.execute("""
        ALTER TABLE comments ADD COLUMN tenant_id uuid;
        UPDATE comments c SET tenant_id = t.tenant_id
            FROM tickets t WHERE t.id = c.ticket_id;
        ALTER TABLE comments ALTER COLUMN tenant_id SET NOT NULL;
        ALTER TABLE tickets ADD CONSTRAINT uq_tickets_tenant_id_id UNIQUE (tenant_id, id);
        ALTER TABLE comments ADD CONSTRAINT fk_comments_tenant_ticket
            FOREIGN KEY (tenant_id, ticket_id)
            REFERENCES tickets (tenant_id, id) NOT VALID;
        ALTER TABLE comments VALIDATE CONSTRAINT fk_comments_tenant_ticket;
    """)
    print("   backfill + UNIQUE(tenant_id, id) + composite FK (NOT VALID -> VALIDATE): ok")

    src = await conn.fetchval(
        "SELECT id FROM tickets WHERE tenant_id = $1 AND number = 300", ids["nordwind"])
    dst = await conn.fetchval(
        "SELECT id FROM tickets WHERE tenant_id = $1 AND number = 300", ids["baltic"])
    try:
        await conn.execute(
            "UPDATE comments SET ticket_id = $1 WHERE ticket_id = $2", dst, src)
    except asyncpg.ForeignKeyViolationError as exc:
        print(f"   the same hostile merge UPDATE -> ForeignKeyViolationError, "
              f"constraint_name={exc.constraint_name!r}")
    print("  => (tenant_id, ticket_id) must exist together in tickets: a comment")
    print("     pointing at another tenant's ticket is now UNREPRESENTABLE (05.4)\n")


# ---------- C. RLS as the read floor -------------------------------------------
APP_DSN = "postgresql://deskhub_app:app_dev@127.0.0.1:55432/deskhub"


async def section_c(conn: asyncpg.Connection, ids: dict[str, str]) -> None:
    print("C. row-level security: the floor under every forgotten WHERE")
    await conn.execute("""
        ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
        ALTER TABLE tickets FORCE ROW LEVEL SECURITY;   -- owners obey too (belt)
        CREATE POLICY tenant_isolation ON tickets
            USING (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid)
            WITH CHECK (tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid);
    """)
    n = await conn.fetchval("SELECT count(*) FROM tickets")
    print(f"   policy + FORCE, queried as the compose user : count(*) = {n:,}   "
          "<- SUPERUSER: policies never apply, FORCE or not")
    await conn.execute("""
        DO $$ BEGIN
            CREATE ROLE deskhub_app LOGIN PASSWORD 'app_dev';
        EXCEPTION WHEN duplicate_object THEN NULL; END $$;
        GRANT USAGE ON SCHEMA public TO deskhub_app;
        GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public
            TO deskhub_app;
    """)
    app = await asyncpg.connect(APP_DSN)               # the role production should use
    try:
        n = await app.fetchval("SELECT count(*) FROM tickets")
        print(f"   as deskhub_app, GUC never set               : count(*) = {n:,}   "
              "<- fail CLOSED, not open")
        await app.execute(f"SET app.tenant_id = '{ids['hansefracht']}'")
        n = await app.fetchval("SELECT count(*) FROM tickets")   # note: no WHERE at all
        print(f"   as deskhub_app, tenant set, no WHERE        : count(*) = {n:,}")
        try:
            await app.execute(
                "INSERT INTO tickets (tenant_id, number, subject) "
                "VALUES ($1, 999001, 'smuggle')", ids["baltic"])
        except asyncpg.InsufficientPrivilegeError as exc:
            print(f"   INSERT a row FOR ANOTHER TENANT             : "
                  f"{exc.message.splitlines()[0]}")
    finally:
        await app.close()
    print("  => the floor exists only for non-superuser roles: the app connects as")
    print("     deskhub_app, never as the owner; a blank GUC means ZERO rows; and")
    print("     WITH CHECK polices writes too (05.4)\n")


# ---------- D. the GUC is connection state -------------------------------------
async def section_d(ids: dict[str, str]) -> None:
    print("D. scoping state vs pooled connections (04.4's bleed, at the DB layer)")
    conn = await asyncpg.connect(APP_DSN)  # ONE server connection = PgBouncer's world
    try:
        await conn.execute(f"SET app.tenant_id = '{ids['nordwind']}'")   # request 1
        n1 = await conn.fetchval("SELECT count(*) FROM tickets")
        n2 = await conn.fetchval("SELECT count(*) FROM tickets")         # request 2:
        print(f"   request 1 (nordwind, session SET): {n1:,} rows")      # forgot to SET
        print(f"   request 2 (NEVER set a tenant)   : {n2:,} rows   <- sees NORDWIND")
        await conn.execute("RESET app.tenant_id")

        async with conn.transaction():                                   # the fix
            await conn.execute(
                f"SET LOCAL app.tenant_id = '{ids['nordwind']}'")
            n1 = await conn.fetchval("SELECT count(*) FROM tickets")
        n2 = await conn.fetchval("SELECT count(*) FROM tickets")
        print(f"   SET LOCAL inside txn             : {n1:,} rows during, "
              f"{n2:,} after commit   <- scope dies with the txn")
    finally:
        await conn.close()

    pool = await asyncpg.create_pool(APP_DSN, min_size=1, max_size=1)
    try:
        async with pool.acquire() as conn:
            await conn.execute(f"SET app.tenant_id = '{ids['nordwind']}'")
        async with pool.acquire() as conn:                    # same physical connection
            setting = await conn.fetchval(
                "SELECT current_setting('app.tenant_id', true)")
        print(f"   asyncpg pool, release + reacquire: current_setting = {setting!r}   "
              "<- the pool's RESET ALL saved us")
    finally:
        await pool.close()
    print("  => session SET leaks tenant scope across whoever shares the connection;")
    print("     asyncpg's pool resets, but transaction-pooling proxies (05.9) do not")
    print("     carry session state - SET LOCAL per transaction is the only shape")
    print("     that composes everywhere (05.4)\n")


# ---------- E. the planner's view ----------------------------------------------
async def section_e(ids: dict[str, str]) -> None:
    print("E. what RLS does to the inbox query's plan")
    conn = await asyncpg.connect(APP_DSN)
    try:
        async with conn.transaction():
            await conn.execute(f"SET LOCAL app.tenant_id = '{ids['hansefracht']}'")
            plan = await conn.fetch("""
                EXPLAIN (ANALYZE, BUFFERS)
                SELECT id, subject FROM tickets
                WHERE status = 'open'
                ORDER BY last_activity_at DESC NULLS LAST LIMIT 50""")
            for line in plan:
                text = line["QUERY PLAN"]
                if any(k in text for k in ("Index Scan", "Index Cond", "Filter",
                                           "Execution Time")):
                    print(f"   {text.strip()}")
    finally:
        await conn.close()
    print("  => the policy predicate becomes an ordinary qual: tenant_id lands in")
    print("     the Index Cond because the index LEADS with it - the 02.5/05.2 rule")
    print("     is what keeps the security floor cheap (05.4)")


async def main() -> None:
    conn = await asyncpg.connect(DSN)
    try:
        ids = await seed(conn)
        await section_a(conn, ids)
        await section_b(conn, ids)
        await section_c(conn, ids)
    finally:
        await conn.close()
    await section_d(ids)
    await section_e(ids)


if __name__ == "__main__":
    asyncio.run(main())
