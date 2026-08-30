"""Lab for 05.2 Normalisation and denormalisation tradeoffs.

Reproduces the notebook's captures against the module compose.yaml (PostgreSQL 18):
  A. the update anomaly, measured: a duplicated assignee_name goes contradictory
     the moment one copy is updated
  B. the 1NF violation: comma-separated tags, LIKE '%vip%' matching 'not-vip',
     and the association-table fix
  C. the "joins are slow" myth: a 3-way join for the 50-row inbox, timed
  D. the query that genuinely justifies a counter: ordering a queue by an
     aggregate (GROUP BY over the comments table) vs an indexed counter column
  E. counter drift under naive app-side maintenance (lost updates + retry
     double-counts + a bulk path that bypasses the app entirely), then the
     trigger version surviving the same traffic, then the trigger's measured cost

Run:  docker compose up -d --wait   (in the module directory), then
      python lab_05_02_normalisation.py
"""
import asyncio
import random
import sys
import time

import asyncpg

if sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DSN = "postgresql://deskhub:deskhub_dev@127.0.0.1:55432/deskhub"

TICKETS = 200_000          # one busy tenant; comments = number % 9 per ticket (~800k)


# ---------- seed: the founding 05.1 schema, at volume --------------------------
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
CREATE INDEX ix_comments_ticket ON comments (ticket_id);   -- FK columns are NOT auto-indexed
"""


async def seed(conn: asyncpg.Connection) -> str:
    print(f"seeding: 1 tenant, 50 agents, {TICKETS:,} tickets, ~{TICKETS * 4:,} comments ...")
    await conn.execute(SCHEMA)
    tenant = await conn.fetchval(
        "INSERT INTO tenants (slug, name) VALUES ('nordwind', 'Nordwind Logistik GmbH') "
        "RETURNING id")
    await conn.execute("""
        INSERT INTO agents (tenant_id, email, display_name)
        SELECT $1, 'agent' || g || '@nordwind.example', 'Agent ' || g
        FROM generate_series(1, 50) g""", tenant)
    await conn.execute("""
        INSERT INTO tickets (tenant_id, number, requester_email, subject, created_at)
        SELECT $1, g, 'requester' || (g % 5000) || '@example.com',
               'Ticket #' || g,
               now() - ((g * 39) % 7776000) * interval '1 second'   -- spread over ~90 days
        FROM generate_series(1, $2) g""", tenant, TICKETS)
    await conn.execute("""
        UPDATE tickets t SET assignee_id = a.id
        FROM (SELECT id, row_number() OVER (ORDER BY id) AS rn FROM agents) a
        WHERE t.number % 50 = a.rn - 1""")
    # number % 9 comments per ticket: ~11% of tickets have none - a real queue shape
    await conn.execute("""
        INSERT INTO comments (ticket_id, author_agent_id, body, created_at)
        SELECT t.id, t.assignee_id, 'reply ' || g,
               least(t.created_at + g * interval '3 hours', now())
        FROM tickets t, generate_series(1, 8) g
        WHERE g <= t.number % 9""")
    await conn.execute("ANALYZE tickets; ANALYZE comments;")
    n = await conn.fetchval("SELECT count(*) FROM comments")
    print(f"seeded: {n:,} comments\n")
    return tenant


# ---------- A. the update anomaly ----------------------------------------------
async def section_a(conn: asyncpg.Connection) -> None:
    print("A. one fact, many rows: duplicate assignee_name onto tickets, then rename")
    await conn.execute("""
        ALTER TABLE tickets ADD COLUMN assignee_name text;
        UPDATE tickets t SET assignee_name = a.display_name
        FROM agents a WHERE a.id = t.assignee_id;
    """)
    # Agent 7 marries; the rename lands on agents, and on the copies... mostly:
    await conn.execute("UPDATE agents SET display_name = 'Anna Weber-Fuchs' "
                       "WHERE display_name = 'Agent 7'")
    await conn.execute("""
        UPDATE tickets SET assignee_name = 'Anna Weber-Fuchs'
        WHERE assignee_id = (SELECT id FROM agents WHERE display_name = 'Anna Weber-Fuchs')
          AND number < 100000""")                # "the fix" - which missed half the rows
    rows = await conn.fetch("""
        SELECT t.assignee_name, count(*) AS tickets
        FROM tickets t JOIN agents a ON a.id = t.assignee_id
        WHERE a.display_name = 'Anna Weber-Fuchs'
        GROUP BY t.assignee_name ORDER BY t.assignee_name""")
    for r in rows:
        print(f"   assignee_name={r['assignee_name']!r:20s}  on {r['tickets']:,} tickets")
    print("  => ONE agent, TWO names, zero errors: every copy of a mutable fact is")
    print("     an update you must never miss. Store the fact once (05.2)")
    await conn.execute("ALTER TABLE tickets DROP COLUMN assignee_name")
    print("     (column dropped - section C shows the join it 'saved' costs nothing)\n")


# ---------- B. 1NF: the comma-separated list -----------------------------------
async def section_b(conn: asyncpg.Connection) -> None:
    print("B. tags as a comma-separated column vs an association table")
    await conn.execute("""
        DROP TABLE IF EXISTS flat_tags, ticket_tags CASCADE;
        CREATE TABLE flat_tags (subject text, tags text);
        INSERT INTO flat_tags VALUES
            ('Printer on fire',  'vip,hardware'),
            ('Password reset',   'not-vip'),
            ('Invoice question', 'billing,vip'),
            ('Slow VPN',         'network');
    """)
    rows = await conn.fetch(
        "SELECT subject, tags FROM flat_tags WHERE tags LIKE '%vip%' ORDER BY subject")
    print("   WHERE tags LIKE '%vip%' returns:")
    for r in rows:
        marker = "   <- WRONG" if "not-vip" in r["tags"] else ""
        print(f"     {r['subject']:18s} tags={r['tags']!r}{marker}")
    await conn.execute("""
        CREATE TABLE ticket_tags (
            subject text, tag text,
            PRIMARY KEY (subject, tag)      -- pure association: the natural key IS the PK
        );
        INSERT INTO ticket_tags
        SELECT subject, unnest(string_to_array(tags, ',')) FROM flat_tags;
    """)
    rows = await conn.fetch(
        "SELECT subject FROM ticket_tags WHERE tag = 'vip' ORDER BY subject")
    print(f"   ticket_tags WHERE tag = 'vip' returns: {[r['subject'] for r in rows]}")
    print("  => a list in a column can only be searched as a substring; one row per")
    print("     fact makes the question exact, indexable and constrainable (05.2)\n")


# ---------- C. the join myth ---------------------------------------------------
async def section_c(conn: asyncpg.Connection, tenant: str) -> None:
    print("C. the 50-row agent inbox as a 3-way join - what does the join cost?")
    plan = await conn.fetch(f"""
        EXPLAIN (ANALYZE, BUFFERS)
        SELECT t.number, t.subject, a.display_name, te.name
        FROM tickets t
        JOIN agents a   ON a.id = t.assignee_id
        JOIN tenants te ON te.id = t.tenant_id
        WHERE t.tenant_id = '{tenant}'
        ORDER BY t.id DESC LIMIT 50""")
    for line in plan:
        text = line["QUERY PLAN"]
        if any(k in text for k in ("Limit", "Execution Time", "Planning Time")):
            print(f"   {text.strip()}")
    print("  => sub-millisecond for 50 joined rows at 200k tickets. The join the")
    print("     duplicated column 'saved' was never the expensive part (05.2)\n")


# ---------- D. the query that DOES justify a counter ---------------------------
QUEUE_BY_AGGREGATE = """
    SELECT t.id, max(c.created_at) AS last_activity
    FROM tickets t LEFT JOIN comments c ON c.ticket_id = t.id
    WHERE t.tenant_id = $1 AND t.status = 'open'
    GROUP BY t.id
    ORDER BY last_activity DESC NULLS LAST LIMIT 50"""


async def section_d(conn: asyncpg.Connection, tenant: str) -> None:
    print("D. 'queue by last activity' - ordering by a DERIVED value, two ways")
    t0 = time.perf_counter()
    await conn.fetch(QUEUE_BY_AGGREGATE, tenant)
    agg_ms = (time.perf_counter() - t0) * 1000
    plan = await conn.fetch(
        "EXPLAIN (ANALYZE) " + QUEUE_BY_AGGREGATE.replace("$1", f"'{tenant}'"))
    for line in plan:
        text = line["QUERY PLAN"]
        if any(k in text for k in ("Aggregate", "Sort", "Seq Scan", "Execution Time")):
            print(f"   {text.strip()}")
    print(f"   aggregate version: {agg_ms:8.1f} ms   <- every open ticket's comments,")
    print("                                         aggregated and sorted, per page view")

    await conn.execute("""
        ALTER TABLE tickets
            ADD COLUMN comment_count    int         NOT NULL DEFAULT 0,
            ADD COLUMN last_activity_at timestamptz;
        UPDATE tickets t SET comment_count = s.n, last_activity_at = s.latest
        FROM (SELECT ticket_id, count(*) AS n, max(created_at) AS latest
              FROM comments GROUP BY ticket_id) s
        WHERE s.ticket_id = t.id;
        CREATE INDEX ix_tickets_tenant_activity
            ON tickets (tenant_id, last_activity_at DESC NULLS LAST);
        ANALYZE tickets;
    """)
    t0 = time.perf_counter()
    await conn.fetch("""
        SELECT id, last_activity_at FROM tickets
        WHERE tenant_id = $1 AND status = 'open'
        ORDER BY last_activity_at DESC NULLS LAST LIMIT 50""", tenant)
    counter_ms = (time.perf_counter() - t0) * 1000
    print(f"   counter version  : {counter_ms:8.1f} ms   <- one indexed read")
    print(f"  => {agg_ms / max(counter_ms, 0.01):,.0f}x. Denormalise when you FILTER or")
    print("     SORT by the derived value - and now the copy needs a writer (05.2)\n")


# ---------- E. who keeps the copy honest? --------------------------------------
async def naive_comment(conn, ticket_id, rng) -> None:
    """The launch-era shape: INSERT, then a separate counter UPDATE from app code."""
    await conn.execute(
        "INSERT INTO comments (ticket_id, body) VALUES ($1, 'naive reply')", ticket_id)
    roll = rng.random()
    if roll < 0.02:
        return                                     # error/deploy between the two writes:
    await conn.execute(                            # the bump is simply lost (03.10)
        "UPDATE tickets SET comment_count = comment_count + 1, last_activity_at = now() "
        "WHERE id = $1", ticket_id)
    if roll > 0.98:                                # webhook redelivered, handler re-ran
        await conn.execute(                        # just the bump: counted twice (02.8)
            "UPDATE tickets SET comment_count = comment_count + 1 WHERE id = $1", ticket_id)


RECONCILE = """
    SELECT count(*) FILTER (WHERE t.comment_count <> s.n)   AS drifted,
           coalesce(sum(abs(t.comment_count - s.n)), 0)     AS total_error
    FROM tickets t
    JOIN LATERAL (SELECT count(*) AS n FROM comments c WHERE c.ticket_id = t.id) s ON true
    WHERE t.number BETWEEN 1000 AND 1999"""


async def section_e(conn: asyncpg.Connection) -> None:
    print("E. counter maintenance: application afterthought vs trigger")
    rng = random.Random(42)
    ids = [r["id"] for r in await conn.fetch(
        "SELECT id FROM tickets WHERE number BETWEEN 1000 AND 1999 ORDER BY number")]
    for ticket_id in ids:
        await naive_comment(conn, ticket_id, rng)
    row = await conn.fetchrow(RECONCILE)
    print(f"   naive app-side, 1,000 comments: {row['drifted']} tickets drifted "
          f"(total error {row['total_error']})")

    await conn.execute("""
        INSERT INTO comments (ticket_id, body)
        SELECT id, 'imported reply' FROM tickets WHERE number BETWEEN 1000 AND 1099""")
    row = await conn.fetchrow(RECONCILE)
    print(f"   + a 100-row bulk import (bypasses the app): {row['drifted']} drifted "
          f"(total error {row['total_error']})")

    await conn.execute("""
        CREATE FUNCTION bump_ticket_activity() RETURNS trigger AS $$
        BEGIN
            UPDATE tickets
            SET comment_count   = comment_count + 1,
                last_activity_at = greatest(coalesce(last_activity_at, NEW.created_at),
                                            NEW.created_at),
                updated_at = now()
            WHERE id = NEW.ticket_id;
            RETURN NEW;
        END $$ LANGUAGE plpgsql;
        CREATE TRIGGER trg_comment_activity
            AFTER INSERT ON comments
            FOR EACH ROW EXECUTE FUNCTION bump_ticket_activity();
    """)
    # repair the drift once; from here the trigger is the only writer (the app-side
    # bump is DELETED in the same change - two writers would double-count)
    await conn.execute("""
        UPDATE tickets t SET comment_count = s.n, last_activity_at = s.latest
        FROM (SELECT ticket_id, count(*) AS n, max(created_at) AS latest
              FROM comments GROUP BY ticket_id) s
        WHERE s.ticket_id = t.id""")
    for ticket_id in ids[:500]:                    # plain inserts: the fixed app path
        await conn.execute(
            "INSERT INTO comments (ticket_id, body) VALUES ($1, 'trigger-era reply')",
            ticket_id)
    await conn.execute("""
        INSERT INTO comments (ticket_id, body)
        SELECT id, 'imported again' FROM tickets WHERE number BETWEEN 1000 AND 1099""")
    row = await conn.fetchrow(RECONCILE)
    print(f"   trigger as the only writer, incl. another bulk import: "
          f"{row['drifted']} drifted (total error {row['total_error']})")

    # honest cost: per-row trigger = one extra UPDATE per insert
    await conn.execute("ALTER TABLE comments DISABLE TRIGGER trg_comment_activity")
    t0 = time.perf_counter()
    await conn.execute("""
        INSERT INTO comments (ticket_id, body)
        SELECT id, 'cost probe' FROM tickets WHERE number BETWEEN 2000 AND 21999""")
    without = time.perf_counter() - t0
    await conn.execute("ALTER TABLE comments ENABLE TRIGGER trg_comment_activity")
    t0 = time.perf_counter()
    await conn.execute("""
        INSERT INTO comments (ticket_id, body)
        SELECT id, 'cost probe' FROM tickets WHERE number BETWEEN 2000 AND 21999""")
    with_trigger = time.perf_counter() - t0
    print(f"   trigger cost: 20,000 inserts  without={without:5.2f}s  "
          f"with={with_trigger:5.2f}s  ({with_trigger / without:.1f}x)")
    print("  => a copy is only as honest as its writer. The trigger fires on EVERY")
    print("     path, bulk imports included - and its price is a real, measured line")
    print("     item on the write path (05.2)")


async def main() -> None:
    conn = await asyncpg.connect(DSN)
    try:
        tenant = await seed(conn)
        await section_a(conn)
        await section_b(conn)
        await section_c(conn, tenant)
        await section_d(conn, tenant)
        await section_e(conn)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
