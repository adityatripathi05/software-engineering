# Module 02 lab

Runnable scripts that reproduce the notebooks' incident mechanisms (AUTHORING-GUIDE §4.4).
Run each with plain `python <script>.py`; everything is in-process (TestClient/ASGITransport,
sqlite, asyncio) — no servers, no infrastructure.

| Script | Notebook | Reproduces |
|---|---|---|
| `lab_02_01_redirects.py` | 02.1 | The trailing-slash 307 · httpx stripping `Authorization` on a cross-host redirect — the intermittent-401 mechanism |
| `lab_02_02_query_cost.py` | 02.2 | Multiplicative resolver fan-out: 1 request, 222 "SQL statements"; a depth limit bounding it before execution (mechanism simulation — no GraphQL stack pinned) |
| `lab_02_03_enum_compat.py` | 02.3 | A closed-Literal "generated SDK" crashing on a new enum value that a tolerant client forwards untouched |
| `lab_02_04_response_types.py` | 02.4 | Nine fields served with zero documented (no declared response type) · the filter · the committed-snapshot diff gate failing on a contract change |
| `lab_02_05_pagination.py` | 02.5 | OFFSET export under head-inserts (sqlite): 41 duplicates, all created-during rows missed, start-set intact · the keyset cursor walking exactly |
| `lab_02_06_sort_registry.py` | 02.6 | Indexed vs unindexed sort on 300k rows (0.1 ms vs 59 ms, query plans shown) · the closed sortable-field registry |
| `lab_02_07_patch_tristate.py` | 02.7 | `model_dump()` erasing untouched fields under 200 OK · `exclude_unset=True` preserving absent/null/valued |
| `lab_02_08_idempotency_keys.py` | 02.8 | The cross-tenant key collision · `(tenant, api_key, key)` scoping · the fingerprint catching same-key-different-payload |
| `lab_02_09_problem_types.py` | 02.9 | A copy edit breaking the detail-parsing client while the `type`-branching client never notices |
| `lab_02_10_operation_handles.py` | 02.10 | The 404-on-fresh-handle amplification loop (4 duplicate jobs from one export) · read-your-writes issuing |
| `lab_02_11_webhook_bulkheads.py` | 02.11 | Head-of-line blocking measured: one hanging destination takes healthy lag from 0.13 s to 1.6 s in a shared pool; per-destination bulkheads isolate it |
| `lab_02_12_quota_classes.py` | 02.12 | A real token bucket: the batch drains the shared bucket and 429s the dashboard; credential-class buckets keep fates separate; `RateLimit-*`/`Retry-After` headers |
| `lab_02_13_removal_gate.py` | 02.13 | 0.05% aggregate = 100% of one client's pipeline · the evidence-gated removal check · the brownout |

Provenance: re-derived from the notebooks' incidents after the §4.4 convention was adopted and
verified on the pinned stack. The 02.5 measurement corrected the notebook's Root Cause geometry
(head-inserts re-serve already-read rows and never visit rows created during the export — the
opposite of "old rows skipped") and strengthened its CI drift test with a no-re-serve assertion.
