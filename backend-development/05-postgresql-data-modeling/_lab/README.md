# Module 05 lab

Runnable scripts that reproduce the notebooks' captured transcripts (AUTHORING-GUIDE §4.4).

This module is the first with real infrastructure: start the module's PostgreSQL first,
from the module directory —

```
docker compose up -d --wait
```

— then run each script with plain `python <script>.py`. The database is deliberately
ephemeral: `docker compose down` resets it, and every script recreates what it needs.

| Script | Notebook | Reproduces |
|---|---|---|
| `lab_05_01_keys.py` | 05.1 | What each key generator produces (v4 scrambles arrival order, v7 preserves it; `uuid_extract_timestamp` reads the v7 timestamp back) · identity gaps after a rollback · the B-tree geometry of 1M ordered vs random keys (build time, WAL, index size, `pgstatindex` leaf density 90% vs ~72%, fragmentation 0% vs ~50%) · steady-state WAL amplification after CHECKPOINT (~3× for the same 100k rows) · what `ORDER BY id DESC LIMIT 100` returns per key type, with the backward index-scan plan · the founding Deskhub schema (tenants/agents/tickets/comments/attachments) created and exercised |
| `lab_05_02_normalisation.py` | 05.2 | The update anomaly measured (one agent, two names across 4,000 rows) · the comma-separated-tags 1NF violation (`LIKE '%vip%'` matching `not-vip`) · the join myth (3-way inbox join: 0.25 ms) · the query that justifies a counter (queue ordered by aggregate: 892 ms vs 3.8 ms indexed counter, 236×) · counter drift under naive two-statement maintenance (42/1,000) and a bulk-import bypass (135 more), then the trigger as sole writer (0 drift) and its measured cost (2.5× on bulk inserts) |
| `lab_05_03_constraints.py` | 05.3 | Garbage statuses accepted by an unconstrained column, then refused with the constraint *name* in the error (03.8's mapping key) · constraining a live 200k-row table: plain `ADD` fails on stock, `NOT VALID` in 3.6 ms, repair 997 rows, `VALIDATE` under the weaker lock · vocabulary evolution three ways (`ALTER TYPE ... DROP VALUE` → "not implemented") · upsert: 20 concurrent check-then-act (1 inserted / 9 violations / 10 stale skips) vs `ON CONFLICT` (one row, all callers get it), the `DO NOTHING RETURNING None` trap, identity burn on conflicts · the gapless allocator: naive max+1 collapsing to 2 distinct numbers, the counter-row upsert issuing 1..20 exactly, a rollback *reusing* its number, and the price — 300 allocations serialised on one tenant (2.5 s) vs spread over ten (0.4 s) · timestamptz vs timestamp (one row, two instants) and float vs numeric money |
| `lab_05_04_tenancy.py` | 05.4 | The cross-tenant *write* the launch schema cannot refuse (a merge UPDATE moving one tenant's internal note onto another tenant's ticket, silently) and the author-vs-ticket audit that finds it · repair, then `tenant_id` on comments + `UNIQUE (tenant_id, id)` + the composite FK — the same hostile UPDATE now fails naming `fk_comments_tenant_ticket` · RLS: superusers bypass policies (FORCE or not), the non-superuser app role fails *closed* on an unset GUC (0 rows), scopes with no WHERE at all, and `WITH CHECK` refuses cross-tenant INSERTs · the GUC as connection state: session `SET` bleeding across two logical requests on one connection, `SET LOCAL` dying with its transaction, asyncpg's pool `RESET ALL` · the policy predicate landing in the inbox plan's `Index Cond` (0.06 ms) |
