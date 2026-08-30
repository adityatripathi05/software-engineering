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
