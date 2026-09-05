"""Lab for 05.6 EXPLAIN and EXPLAIN ANALYZE.

Reproduces the notebook's captures against the module compose.yaml (PostgreSQL 18):
  A. anatomy of a plan: cost / rows / width, and the seq-scan cost derived by
     hand from pg_class and the five cost GUCs - matching the planner's number
  B. estimates vs actuals: the functional-dependency misestimate (tenant ->
     agent), and what `loops` really means (per-loop averages, not totals)
  C. the node zoo by selectivity: the same table answered by Index Scan,
     Bitmap Heap Scan and Parallel Seq Scan as the predicate widens
  D. BUFFERS: shared hit vs read, and why a big seq scan keeps "reading"
  E. memory: Sort spilling to disk and Hash Join batching under work_mem,
     and the same plan with the memory it needed
  F. the plan your app runs: prepared statements, custom vs generic plans,
     pg_prepared_statements, EXPLAIN (GENERIC_PLAN), and what forcing the
     generic plan does to the partial inbox index
  G. auto_explain: the plan of a slow statement, as the server logs it
  H. what EXPLAIN ANALYZE does not measure: a timeline query whose plan runs
     in ~1 ms while the client waits hundreds of ms - the ERP-dump comment
     bodies, EXPLAIN (ANALYZE, SERIALIZE), and the projection fix; plus
     EXPLAIN ANALYZE on DML inside a rolled-back transaction

RLS from 05.4 is deliberately NOT enabled here, to keep planner output about
plan reading alone (05.4 captured the policy qual folding into plans).

Run:  docker compose up -d --wait   (in the module directory), then
      python lab_05_06_explain.py
"""
import asyncio
import subprocess
import sys
import time

import asyncpg

if sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DSN = "postgresql://deskhub:deskhub_dev@127.0.0.1:55432/deskhub"


MODULE_DIR = __import__("pathlib").Path(__file__).resolve().parent.parent


def psql(sql: str) -> str:
    """Run one statement through the container's psql (for EXPLAIN (GENERIC_PLAN),
    which needs unbound $n parameters - asyncpg insists on binding them)."""
    try:
        return subprocess.run(
            ["docker", "compose", "exec", "-T", "postgres", "psql", "-U", "deskhub",
             "-d", "deskhub", "-X", "-c", sql],
            capture_output=True, text=True, timeout=60, cwd=MODULE_DIR).stdout
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"(psql unavailable: {exc})"


def docker_logs(since: float) -> str:
    """The server log (stderr of the compose container) since a unix timestamp."""
    try:
        return subprocess.run(
            ["docker", "compose", "logs", "postgres", "--no-log-prefix",
             "--since", f"{int(since) - 1}"],
            capture_output=True, text=True, timeout=30, cwd=MODULE_DIR).stdout
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"(could not read docker logs: {exc})"


async def explain(conn, sql: str, *args, opts="ANALYZE, BUFFERS", keys=None,
                  indent="   ") -> list[str]:
    """Print an EXPLAIN, optionally only the lines containing one of `keys`."""
    rows = await conn.fetch(f"EXPLAIN ({opts}) " + sql, *args)
    lines = [r["QUERY PLAN"] for r in rows]
    for text in lines:
        if keys is None or any(k in text for k in keys):
            print(f"{indent}{text}")
    return lines


# ---------- seed ---------------------------------------------------------------
async def seed(conn: asyncpg.Connection) -> dict:
    print("seeding: Nordwind 400k tickets / 60 agents, HanseFracht + Baltic 5k / 5 agents,")
    print("         ~1.2M comments, and one ERP-integration ticket with 40 dump comments ...")
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
        WITH (fillfactor = 90);
        CREATE TABLE comments (
            id uuid PRIMARY KEY DEFAULT uuidv7(),
            tenant_id uuid NOT NULL,
            ticket_id uuid NOT NULL,
            author_id uuid,
            body text NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            CONSTRAINT uq_comments_tenant_id_id UNIQUE (tenant_id, id),
            CONSTRAINT fk_comments_tenant_ticket
                FOREIGN KEY (tenant_id, ticket_id)
                REFERENCES tickets (tenant_id, id));
    """)
    ids: dict = {}
    for slug in ("nordwind", "hansefracht", "baltic"):
        ids[slug] = await conn.fetchval(
            "INSERT INTO tenants (slug) VALUES ($1) RETURNING id", slug)
    for slug, n_agents in (("nordwind", 60), ("hansefracht", 5), ("baltic", 5)):
        await conn.execute("""
            INSERT INTO agents (tenant_id, email)
            SELECT $1, 'agent' || g || '@' || $2 || '.example'
            FROM generate_series(1, $3) g""", ids[slug], slug, n_agents)
    for slug, n_tickets in (("nordwind", 400_000), ("hansefracht", 5_000),
                            ("baltic", 5_000)):
        n_agents = 60 if slug == "nordwind" else 5
        await conn.execute("""
            INSERT INTO tickets (tenant_id, number, requester_email, subject, status,
                                 assignee_id, comment_count, last_activity_at)
            SELECT $1, g,
                   'requester' || (g % 9000) || '@example.com',
                   'Ticket #' || g,
                   CASE WHEN g % 5 = 0 THEN 'open'
                        WHEN g % 7 = 0 THEN 'pending' ELSE 'solved' END,
                   a.id,
                   1 + (g % 4),   -- not % 5: that would correlate with assignee
                   now() - ((g * 13) % 7776000) * interval '1 second'
            FROM generate_series(1, $2) g
            JOIN (SELECT id, row_number() OVER (ORDER BY id) rn FROM agents
                  WHERE tenant_id = $1) a
              ON a.rn = 1 + (g * 7) % $3""", ids[slug], n_tickets, n_agents)
    # ~3 short comments per ticket (comment_count is set directly above; the
    # 05.2 trigger is not installed here - this lab is about reading plans)
    await conn.execute("""
        INSERT INTO comments (tenant_id, ticket_id, author_id, body, created_at)
        SELECT t.tenant_id, t.id, t.assignee_id,
               'Follow-up ' || g || ' on ticket ' || t.number,
               t.last_activity_at - (6 - g) * interval '1 hour'
        FROM tickets t, generate_series(1, 5) g
        WHERE g <= t.comment_count""")
    # The ERP-integration ticket: 40 comments, each a ~300 KB sync-payload dump
    erp = await conn.fetchval(
        "SELECT id FROM tickets WHERE tenant_id = $1 AND number = 388214",
        ids["nordwind"])
    await conn.execute("""
        INSERT INTO comments (tenant_id, ticket_id, author_id, body, created_at)
        SELECT $1, $2, NULL,
               (SELECT string_agg(format('%s sync order=%s sku=%s qty=%s status=%s',
                        '2027-01-26T18:' || lpad((l / 60)::text, 2, '0') || ':'
                            || lpad((l % 60)::text, 2, '0') || 'Z',
                        4000000 + l * 7, 'NW-' || (l * 31 % 9973), l % 40,
                        (ARRAY['ok','retry','skipped'])[1 + l % 3]), E'\\n')
                FROM generate_series(1, 5000) l),
               now() - (40 - g) * interval '3 minute'
        FROM generate_series(1, 40) g""", ids["nordwind"], erp)
    await conn.execute("UPDATE tickets SET comment_count = 43 WHERE id = $1", erp)
    # Agent 42 is 05.5's sparse case again: a cleared queue, 3 open tickets left
    sparse = await conn.fetchval("""
        SELECT id FROM (SELECT id, row_number() OVER (ORDER BY id) rn FROM agents
                        WHERE tenant_id = $1) a WHERE rn = 42""", ids["nordwind"])
    await conn.execute("""
        UPDATE tickets SET status = 'solved'
        WHERE tenant_id = $1 AND assignee_id = $2 AND status IN ('open','pending')
          AND number NOT IN (SELECT number FROM tickets
                             WHERE tenant_id = $1 AND assignee_id = $2
                               AND status IN ('open','pending')
                             ORDER BY last_activity_at ASC LIMIT 3)""",
        ids["nordwind"], sparse)
    ids["sparse"] = sparse
    await conn.execute("""
        CREATE INDEX ix_tickets_tenant_activity
            ON tickets (tenant_id, last_activity_at DESC NULLS LAST);
        CREATE INDEX ix_tickets_inbox
            ON tickets (tenant_id, assignee_id, last_activity_at DESC NULLS LAST)
            WHERE status IN ('open','pending');
        CREATE INDEX ix_comments_tenant_ticket
            ON comments (tenant_id, ticket_id, created_at);
    """)
    # VACUUM cannot run inside the implicit transaction of a multi-statement string
    await conn.execute("VACUUM ANALYZE tenants, agents, tickets, comments")
    ids["erp_ticket"] = erp
    ids["hanse_agent"] = await conn.fetchval(
        "SELECT id FROM agents WHERE tenant_id = $1 ORDER BY id LIMIT 1",
        ids["hansefracht"])
    ids["busy"] = await conn.fetchval("""
        SELECT assignee_id FROM tickets
        WHERE tenant_id = $1 AND status IN ('open','pending')
        GROUP BY assignee_id ORDER BY count(*) DESC LIMIT 1""", ids["nordwind"])
    print("seeded\n")
    return ids


# ---------- A. anatomy: cost, rows, width - and the cost derived by hand -------
async def section_a(conn) -> None:
    print("A. anatomy of a plan - EXPLAIN without ANALYZE is the planner's estimate")
    sql = "SELECT count(*) FROM tickets WHERE status = 'pending'"
    print("   -- parallelism off, to see the cost model in one node:")
    await conn.execute("SET max_parallel_workers_per_gather = 0")
    await explain(conn, sql, opts="COSTS")
    stats = await conn.fetchrow(
        "SELECT relpages, reltuples FROM pg_class WHERE relname = 'tickets'")
    gucs = {}
    for g in ("seq_page_cost", "cpu_tuple_cost", "cpu_operator_cost"):
        gucs[g] = float(await conn.fetchval(f"SHOW {g}"))
    pages, tuples = stats["relpages"], stats["reltuples"]
    cost = (pages * gucs["seq_page_cost"] + tuples * gucs["cpu_tuple_cost"]
            + tuples * gucs["cpu_operator_cost"])
    sel = await conn.fetchval("""
        SELECT f FROM pg_stats, unnest(most_common_vals::text::text[],
                                       most_common_freqs) AS m(v, f)
        WHERE tablename = 'tickets' AND attname = 'status' AND v = 'pending'""")
    print(f"   by hand: relpages={pages} reltuples={tuples:.0f}")
    print(f"     seq scan cost = pages*seq_page_cost + tuples*cpu_tuple_cost "
          f"+ tuples*cpu_operator_cost")
    print(f"                   = {pages}*{gucs['seq_page_cost']} + {tuples:.0f}*"
          f"{gucs['cpu_tuple_cost']} + {tuples:.0f}*{gucs['cpu_operator_cost']} "
          f"= {cost:.2f}")
    print(f"     rows = reltuples * MCV freq('pending') = {tuples:.0f} * {sel:.4f} "
          f"= {tuples * sel:.0f}")
    print("   -- parallelism back on: the same scan split across workers:")
    await conn.execute("RESET max_parallel_workers_per_gather")
    await explain(conn, sql, opts="COSTS")
    print(f"     parallel divisor for 2 workers = 2 + (1 - 0.3*2) = 2.4;"
          f" disk cost is NOT divided, cpu cost is:")
    print(f"     {pages} + ({tuples:.0f}*{gucs['cpu_tuple_cost']} + {tuples:.0f}"
          f"*{gucs['cpu_operator_cost']})/2.4 = "
          f"{pages + (tuples * (gucs['cpu_tuple_cost'] + gucs['cpu_operator_cost'])) / 2.4:.2f}")
    print("  => cost is arithmetic over pg_class statistics and five GUCs - not time,")
    print("     not I/O; a unit whose only meaning is 'compared to the other plans")
    print("     for this query'. `rows` is the estimate every decision rests on (05.6)\n")


# ---------- B. estimates vs actuals, and loops ---------------------------------
async def section_b(conn, ids) -> None:
    print("B. estimates vs actuals - the functional-dependency misestimate")
    sql = """
        SELECT t.number, c.body FROM tickets t
        JOIN comments c ON c.tenant_id = t.tenant_id AND c.ticket_id = t.id
        WHERE t.tenant_id = $1 AND t.assignee_id = $2"""
    print("   -- one HanseFracht agent's tickets with their comments:")
    lines = await explain(conn, sql, ids["hansefracht"], ids["hanse_agent"],
                          keys=("Nested Loop", "Hash", "Index", "Seq Scan",
                                "rows=", "Execution Time", "Filter"))
    print("  => tenant_id and assignee_id are not independent (an agent belongs to")
    print("     ONE tenant), but the planner multiplies their selectivities as if")
    print("     they were: est = 410k * P(hanse) * P(this agent). Read `rows=`")
    print("     estimated vs actual on the tickets node - that gap is the lie every")
    print("     node above it is built on. (Fixing it is 05.7's CREATE STATISTICS.)")
    print("   -- `loops`: actual rows and time on the inner side are PER-LOOP averages:")
    for text in lines:
        if "loops=" in text and "loops=1)" not in text:
            print(f"      {text.strip()}")
    print("     total inner rows = rows x loops; total inner time = time x loops.")
    print("     A node reporting 'rows=3 time=0.02' can be the most expensive thing")
    print("     in the plan if loops=40,000 (05.6)\n")


# ---------- C. the node zoo by selectivity -------------------------------------
async def section_c(conn, ids) -> None:
    print("C. the node zoo - one table, one index, three selectivities")
    n = ids["nordwind"]
    cases = [("6 hours", "interval '6 hours'"), ("3 days", "interval '3 days'"),
             ("30 days", "interval '30 days'")]
    for label, window in cases:
        print(f"   -- comment volume on tickets active in the last {label}:")
        await explain(conn,
            f"SELECT sum(comment_count) FROM tickets WHERE tenant_id = $1 "
            f"AND last_activity_at > now() - {window}", n, opts="ANALYZE, COSTS",
            keys=("Scan", "Heap Blocks", "Rows Removed", "Execution Time"),
            indent="      ")
    print("  => the planner picks the access method from the estimated FRACTION of")
    print("     the table: a few rows -> Index Scan (one random heap page per row);")
    print("     a few percent -> Bitmap (collect matching pages first, then read")
    print("     each once, in order); most of it -> Seq Scan, parallel if big enough.")
    print("     No node is 'bad'; each is wrong outside its fraction (05.6)")
    print("   -- Index Only Scan: everything the query needs is in the index:")
    await explain(conn,
        "SELECT count(*) FROM tickets WHERE tenant_id = $1 AND assignee_id = $2 "
        "AND status IN ('open','pending')", n, ids["busy"],
        keys=("Scan", "Heap Fetches", "Execution Time", "Buffers"))
    print("  => 'Heap Fetches: 0' is the visibility map holding (05.5 D)\n")


# ---------- D. buffers: hit vs read ---------------------------------------------
async def section_d(conn) -> None:
    print("D. BUFFERS - shared hit vs read on a table bigger than shared_buffers")
    size = await conn.fetchval("SELECT pg_relation_size('comments')")
    sb = await conn.fetchval("SHOW shared_buffers")
    print(f"   comments heap = {size/1024/1024:.0f} MiB, shared_buffers = {sb}")
    for i in (1, 2):
        print(f"   -- seq scan #{i}:")
        await explain(conn, "SELECT count(*) FROM comments WHERE body LIKE 'Follow-up 2%'",
                      keys=("Seq Scan", "Buffers", "Execution Time"), indent="      ")
    print("  => `read` = not in shared_buffers (served by the OS cache or disk).")
    print("     A seq scan of a table over 1/4 of shared_buffers uses a small ring")
    print("     buffer on purpose, so it keeps READING on every pass instead of")
    print("     evicting the working set to cache itself. hit/read is about")
    print("     PostgreSQL's cache, not the machine's (05.6)\n")


# ---------- E. memory: sort spills and hash batches ----------------------------
async def section_e(conn, ids) -> None:
    print("E. memory - the same plans under work_mem = 4MB and 64MB")
    sort_sql = ("SELECT number, subject FROM tickets WHERE tenant_id = $1 "
                "ORDER BY subject")
    join_sql = ("SELECT count(*) FROM tickets t JOIN comments c "
                "ON c.tenant_id = t.tenant_id AND c.ticket_id = t.id "
                "WHERE t.tenant_id = $1 AND t.status IN ('open','pending')")
    for wm in ("4MB", "64MB"):
        async with conn.transaction():
            await conn.execute(f"SET LOCAL work_mem = '{wm}'")
            # parallelism off so the hash lives in one node; batching is the point
            await conn.execute("SET LOCAL max_parallel_workers_per_gather = 0")
            print(f"   -- work_mem = {wm}: ORDER BY subject over 400k rows")
            await explain(conn, sort_sql, ids["nordwind"], opts="ANALYZE",
                          keys=("Sort Method", "temp", "Execution Time"),
                          indent="      ")
            print(f"   -- work_mem = {wm}: the same sort under COLLATE \"C\"")
            await explain(conn, sort_sql + ' COLLATE "C"', ids["nordwind"],
                          opts="ANALYZE", keys=("Sort Method", "Execution Time"),
                          indent="      ")
            print(f"   -- work_mem = {wm}: hash join of the open/pending working set to comments")
            await explain(conn, join_sql, ids["nordwind"],
                          keys=("Hash Join", "Buckets", "temp", "Execution Time"),
                          indent="      ")
    print("  => 'external merge  Disk' and 'Batches: N>1' say a node ran out of")
    print("     work_mem; `temp read/written` is the bill. But read the TIME next to")
    print("     the method: here the in-memory quicksort is slower than the spill")
    print("     (cache misses over a 28 MB array vs 4 MB runs; temp files sitting in")
    print("     the OS page cache), and the collation costs 5x more than the spill")
    print("     ever did. work_mem is per sort/hash node per query, not per")
    print("     connection - set it per role/statement, never globally (05.6, 17.x)\n")


# ---------- F. the plan your app runs: custom vs generic ------------------------
INBOX_PARAM = """
    SELECT id, subject, last_activity_at FROM tickets
    WHERE tenant_id = $1 AND assignee_id = $2 AND status = ANY($3::text[])
    ORDER BY last_activity_at DESC NULLS LAST LIMIT 50"""


async def section_f(conn, ids) -> None:
    print("F. the plan your app runs - prepared statements and the plan cache")
    n, busy = ids["nordwind"], ids["busy"]
    stmt = await conn.prepare(INBOX_PARAM)   # asyncpg prepares every query anyway
    for i in range(1, 8):
        t0 = time.perf_counter()
        rows = await stmt.fetch(n, busy, ["open", "pending"])
        dt = (time.perf_counter() - t0) * 1000
        ps = await conn.fetchrow("""
            SELECT generic_plans, custom_plans FROM pg_prepared_statements
            WHERE statement = $1""", INBOX_PARAM)
        print(f"   run {i}: {dt:6.2f} ms  rows={len(rows)}  "
              f"custom_plans={ps['custom_plans']} generic_plans={ps['generic_plans']}")
    print("   -- the plan PostgreSQL would use if it went generic (PG16+, via psql):")
    for line in psql("EXPLAIN (GENERIC_PLAN) " + INBOX_PARAM).splitlines():
        if any(k in line for k in ("Limit", "Index", "Filter")):
            print(f"   {line.rstrip()}")
    print("   -- vs the custom plan for these parameters:")
    await explain(conn, INBOX_PARAM, n, busy, ["open", "pending"], opts="COSTS",
                  keys=("Limit", "Index"))
    print("  => a generic plan cannot prove `status = ANY($3)` implies the partial")
    print("     index's WHERE, so it falls back to the activity index + Filter. The")
    print("     plan cache compares ESTIMATED costs after 5 custom runs and, here,")
    print("     keeps re-planning - protection by arithmetic, not by guarantee.")
    print("   -- what it looks like when the generic plan wins: 05.5's sparse agent,")
    print("      generic vs custom, through PREPARE/EXECUTE in psql:")
    script = (
        "SET plan_cache_mode = force_generic_plan; "
        f"PREPARE inbox(uuid, uuid, text[]) AS {INBOX_PARAM}; "
        f"EXPLAIN (ANALYZE, COSTS OFF) EXECUTE inbox('{n}', '{ids['sparse']}', "
        "'{open,pending}'); "
        "SET plan_cache_mode = force_custom_plan; "
        f"EXPLAIN (ANALYZE, COSTS OFF) EXECUTE inbox('{n}', '{ids['sparse']}', "
        "'{open,pending}');")
    for line in psql(script).splitlines():
        if any(k in line for k in ("Index Scan", "Rows Removed", "Buffers: shared",
                                   "Execution Time")):
            print(f"      {line.rstrip()}")
    print("  => EXPLAIN in psql shows you A plan. pg_prepared_statements'")
    print("     generic_plans/custom_plans and EXPLAIN (GENERIC_PLAN) show you")
    print("     whether your app is running THAT plan (05.6; PgBouncer in 05.9)\n")


# ---------- G. auto_explain -----------------------------------------------------
async def section_g(conn, ids) -> None:
    print("G. auto_explain - the plan of a slow statement, as the server logs it")
    await conn.execute("""
        LOAD 'auto_explain';
        SET auto_explain.log_min_duration = '5ms';
        SET auto_explain.log_analyze = on;
        SET auto_explain.log_buffers = on;
        SET auto_explain.log_timing = off;   -- keep the overhead down in production
    """)
    since = time.time()
    await conn.fetch(
        "SELECT count(*) FROM tickets WHERE tenant_id = $1 AND status = 'pending'",
        ids["nordwind"])
    await conn.fetch("SELECT subject FROM tickets WHERE id = $1", ids["erp_ticket"])
    await asyncio.sleep(0.5)
    shown = 0
    for line in docker_logs(since).splitlines():
        if ("duration:" in line or "Query Text" in line or "Query Parameters" in line
                or "Seq Scan" in line or "Filter:" in line or "Rows Removed" in line):
            print(f"   {line.rstrip()}")
            shown += 1
            if shown > 8:
                break
    print("  => only the slow statement was logged; the sub-millisecond lookup was not.")
    print("     auto_explain is EXPLAIN ANALYZE for the statements you did not")
    print("     think to explain, with the parameters that were actually slow (05.6)\n")


# ---------- H. what EXPLAIN ANALYZE does not measure ----------------------------
TIMELINE = """
    SELECT c.id, c.author_id, c.body, c.created_at FROM comments c
    WHERE c.tenant_id = $1 AND c.ticket_id = $2 ORDER BY c.created_at"""
TIMELINE_LEAN = """
    SELECT c.id, c.author_id, left(c.body, 200) AS preview,
           pg_column_size(c.body) AS stored_bytes, c.created_at FROM comments c
    WHERE c.tenant_id = $1 AND c.ticket_id = $2 ORDER BY c.created_at"""
DUMP_BODY = "\n".join(f"2027-01-26T18:{i // 60:02d}:{i % 60:02d}Z sync order={4000000 + i}"
                      for i in range(5000))


async def section_h(conn, ids) -> None:
    print("H. what EXPLAIN ANALYZE does not measure - the ERP ticket's timeline")
    n, erp = ids["nordwind"], ids["erp_ticket"]
    sizes = await conn.fetchrow("""
        SELECT pg_size_pretty(pg_relation_size('comments')) AS heap,
               pg_size_pretty(pg_total_relation_size('comments')
                              - pg_relation_size('comments')
                              - pg_indexes_size('comments')) AS toast,
               (SELECT pg_size_pretty(sum(octet_length(body))::bigint)
                FROM comments WHERE ticket_id = $1) AS ticket_bodies""", erp)
    print(f"   comments heap {sizes['heap']}, TOAST {sizes['toast']}; this ticket's "
          f"43 bodies total {sizes['ticket_bodies']}")
    print("   -- EXPLAIN ANALYZE, the way everyone runs it:")
    await explain(conn, TIMELINE, n, erp,
                  keys=("Index Scan", "Sort", "Buffers", "Execution Time"))
    for label in ("client-side fetch #1", "client-side fetch #2"):
        t0 = time.perf_counter()
        rows = await conn.fetch(TIMELINE, n, erp)
        dt = (time.perf_counter() - t0) * 1000
        total = sum(len(r["body"]) for r in rows)
        print(f"   {label}: {dt:7.1f} ms for {len(rows)} rows, "
              f"{total/1024/1024:.1f} MiB of body")
    print("   -- the server's own log of that fetch (log_min_duration_statement + auto_explain):")
    await conn.execute("""
        SET log_min_duration_statement = 0;
        SET auto_explain.log_min_duration = 0;
        SET auto_explain.log_analyze = on;
        SET auto_explain.log_timing = on;
    """)
    since = time.time()
    await conn.fetch(TIMELINE, n, erp)
    await conn.execute("RESET log_min_duration_statement; RESET auto_explain.log_min_duration")
    await asyncio.sleep(0.5)
    log = docker_logs(since).splitlines()
    starts = [i for i, ln in enumerate(log) if "execute __asyncpg" in ln]
    for line in log[starts[-1]:] if starts else log:
        if "execute __asyncpg" in line or "plan:" in line or "Index Scan" in line:
            print(f"      {line.rstrip()[:150]}")
    print("   -- EXPLAIN (ANALYZE, SERIALIZE): now the output is produced too (PG17+):")
    await explain(conn, TIMELINE, n, erp, opts="ANALYZE, SERIALIZE",
                  keys=("Index Scan", "Buffers", "Serialization", "Execution Time"))
    print("   -- the fix: the list view never needed the body")
    await explain(conn, TIMELINE_LEAN, n, erp, opts="ANALYZE, SERIALIZE",
                  keys=("Serialization", "Execution Time"))
    t0 = time.perf_counter()
    rows = await conn.fetch(TIMELINE_LEAN, n, erp)
    dt = (time.perf_counter() - t0) * 1000
    print(f"   client-side fetch (lean): {dt:6.1f} ms for {len(rows)} rows")
    print("  => EXPLAIN ANALYZE runs the plan and DISCARDS the output: columns the")
    print("     plan never touches are never detoasted, decompressed or converted.")
    print("     The wire, the TOAST reads and the client decode are all outside it.")
    print("     SERIALIZE measures the first two; the app's own timer is the truth (05.6)")

    print("   -- closing the input (05.3): a body-size constraint, NOT VALID first")
    await conn.execute("""
        ALTER TABLE comments ADD CONSTRAINT ck_comments_body_size
            CHECK (octet_length(body) <= 65536) NOT VALID""")
    try:
        await conn.execute("ALTER TABLE comments VALIDATE CONSTRAINT ck_comments_body_size")
    except asyncpg.CheckViolationError as exc:
        print(f"      VALIDATE -> {exc}")
    try:
        await conn.execute("""
            INSERT INTO comments (tenant_id, ticket_id, body)
            VALUES ($1, $2, $3)""", n, erp, DUMP_BODY)
    except asyncpg.CheckViolationError as exc:
        print(f"      next 300 KB dump -> {exc.constraint_name}: refused")
    print("  => new dumps are refused by name (03.8's mapping key); the 40 existing")
    print("     ones are a backfill into attachments, then VALIDATE (05.3's two-step)")

    print("   -- EXPLAIN ANALYZE executes DML for real: wrap it, then roll back")
    await conn.execute("BEGIN")
    await explain(conn,
        "UPDATE tickets SET priority = 'high' WHERE tenant_id = $1 "
        "AND assignee_id = $2 AND status = 'open'", n, ids["busy"],
        opts="ANALYZE, WAL, COSTS OFF",
        keys=("Update", "WAL", "Execution Time"))
    changed = await conn.fetchval(
        "SELECT count(*) FROM tickets WHERE tenant_id = $1 AND assignee_id = $2 "
        "AND priority = 'high'", n, ids["busy"])
    print(f"      inside the transaction: {changed} rows now 'high'")
    await conn.execute("ROLLBACK")
    changed = await conn.fetchval(
        "SELECT count(*) FROM tickets WHERE tenant_id = $1 AND assignee_id = $2 "
        "AND priority = 'high'", n, ids["busy"])
    print(f"      after ROLLBACK: {changed} rows 'high'")
    print("  => ANALYZE means EXECUTE. On INSERT/UPDATE/DELETE that is a write, with")
    print("     WAL and triggers; BEGIN ... EXPLAIN ANALYZE ... ROLLBACK, always (05.6)")


async def main() -> None:
    conn = await asyncpg.connect(DSN)
    try:
        ids = await seed(conn)
        await section_a(conn)
        await section_b(conn, ids)
        await section_c(conn, ids)
        await section_d(conn)
        await section_e(conn, ids)
        await section_f(conn, ids)
        await section_g(conn, ids)
        await section_h(conn, ids)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
