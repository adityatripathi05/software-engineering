"""Lab for 02.8 Idempotency keys.

Reproduces the cross-tenant collision: a store keyed by the RAW client key
treats two tenants' `invoice-001` as the same request — tenant B receives
tenant A's stored invoice. The fix: scope = (tenant, api_key, key), plus a
request fingerprint so same-key-different-payload is a 422, not a replay.
"""
import hashlib
import json

# ---- the incident: global key namespace -------------------------------------
naive_store: dict[str, str] = {}


def create_naive(tenant: str, key: str, payload: dict) -> str:
    if key in naive_store:
        return f"REPLAY of {naive_store[key]}"
    invoice = f"inv_{tenant}_{len(naive_store)}"
    naive_store[key] = invoice
    return f"CREATED {invoice}"


print("-- keys assumed globally unique (clients 'always send UUIDs') --")
print("  tenant A, Idempotency-Key: invoice-001 ->",
      create_naive("A", "invoice-001", {"total": "4200.00"}))
print("  tenant B, Idempotency-Key: invoice-001 ->",
      create_naive("B", "invoice-001", {"total": "9.99"}))
print("  => tenant B just received TENANT A's invoice (02.8)\n")

# ---- the fix: scoped key + fingerprint --------------------------------------
scoped_store: dict[tuple, tuple[str, str]] = {}


def fingerprint(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:12]


def create_scoped(tenant: str, api_key: str, key: str, payload: dict) -> str:
    scope = (tenant, api_key, key)
    fp = fingerprint(payload)
    if scope in scoped_store:
        stored_fp, invoice = scoped_store[scope]
        if stored_fp != fp:
            return "422 problem: idempotency key reused with a DIFFERENT payload"
        return f"REPLAY of {invoice} (same payload — safe)"
    invoice = f"inv_{tenant}_{len(scoped_store)}"
    scoped_store[scope] = (fp, invoice)
    return f"CREATED {invoice}"


print("-- scope (tenant, api_key, key) + payload fingerprint --")
print("  A/key_A/invoice-001 {4200} ->", create_scoped("A", "key_A", "invoice-001", {"total": "4200.00"}))
print("  B/key_B/invoice-001 {9.99} ->", create_scoped("B", "key_B", "invoice-001", {"total": "9.99"}))
print("  A retry, same payload      ->", create_scoped("A", "key_A", "invoice-001", {"total": "4200.00"}))
print("  A same key, NEW payload    ->", create_scoped("A", "key_A", "invoice-001", {"total": "5000.00"}))
print("\n=> client-supplied identifiers live in the CLIENT's namespace; the")
print("   fingerprint catches reuse-with-different-payload as a client bug (02.8).")
