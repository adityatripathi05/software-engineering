"""Lab for 02.2 REST vs RPC vs GraphQL vs gRPC.

Mechanism simulation (no GraphQL library on the pinned stack): a resolver graph
that permits cycles, walked five levels deep by ONE request. The counter plays
the database; the point is the shape of the number — multiplicative in page
sizes — while every request-denominated defence sees exactly 1.

# illustrative - mechanism simulation, not a captured GraphQL stack
"""
SQL_STATEMENTS = {"count": 0}
PAGE = 10        # default page size per relationship


def resolve(entity: str, depth: int) -> int:
    """Walk invoice -> customer -> contacts -> customer -> invoices -> lines."""
    SQL_STATEMENTS["count"] += 1                  # one SELECT per resolver call
    if depth == 0:
        return 1
    children = {"invoice": ["customer"], "customer": ["contact"] * PAGE,
                "contact": ["customer"],           # ← the cycle: back up the graph
                }.get(entity, [])
    total = 1
    for child in children:
        total += resolve("customer" if child == "customer" else child, depth - 1)
    return total


requests_seen_by_rate_limiter = 1                 # the whole query is ONE request
nodes = resolve("invoice", depth=5)

print(f"one 'account overview' query, depth 5, page size {PAGE}:")
print(f"  requests the rate limiter counted : {requests_seen_by_rate_limiter}")
print(f"  resolver calls / SQL statements   : {SQL_STATEMENTS['count']:,}")
print(f"  cost shape: ~PAGE^cycles = {PAGE}^n — multiplicative, chosen by the CLIENT")
print("\n=> every defence you own is denominated in requests; the work is not (02.2).")
print("   Controls that were missing: a depth limit, a complexity budget evaluated")
print("   BEFORE execution, and a result-size cap.")

MAX_DEPTH = 3
print(f"\nwith a depth limit of {MAX_DEPTH}: ", end="")
SQL_STATEMENTS["count"] = 0
resolve("invoice", depth=MAX_DEPTH)
print(f"{SQL_STATEMENTS['count']:,} statements — bounded before execution, not after")
