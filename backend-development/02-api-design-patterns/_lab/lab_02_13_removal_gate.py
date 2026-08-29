"""Lab for 02.13 Deprecation and sunset.

Reproduces the incident's detection failure with numbers: aggregate telemetry
says v1 is 0.05% of traffic — noise; the per-client view says it is 100% of
one customer's pipeline. Then the evidence-gated removal check and the
brownout that forces silent clients to surface before the hard stop.
"""
import random

random.seed(1)          # deterministic transcript

# a day of traffic: (client, api_version)
traffic = [("dashboard-users", "v2")] * 180_000 + [("erp-integrations", "v2")] * 19_900
traffic += [("nordwind-pipeline", "v1")] * 100          # 0.05% — one customer, all v1

total = len(traffic)
v1_total = sum(1 for _, v in traffic if v == "v1")
print(f"aggregate view: v1 = {v1_total}/{total} requests = {v1_total/total:.2%}  "
      "('basically nobody')")

per_client: dict[str, dict[str, int]] = {}
for client, ver in traffic:
    per_client.setdefault(client, {}).setdefault(ver, 0)
    per_client[client][ver] += 1

print("\nper-client view of the same day:")
for client, versions in per_client.items():
    v1 = versions.get("v1", 0)
    share = v1 / sum(versions.values())
    print(f"  {client:20} v1 share of THEIR traffic: {share:6.1%}"
          + ("   ⚠️ their whole pipeline" if share == 1.0 else ""))


def removal_gate(per_client: dict[str, dict[str, int]]) -> str:
    blockers = [c for c, v in per_client.items() if v.get("v1", 0) > 0]
    if blockers:
        return (f"BLOCKED: {len(blockers)} client(s) still on v1: {blockers} — "
                "removal is gated on evidence, not on the calendar")
    return "CLEAR: zero v1 usage measured; removal may proceed"


print("\nrelease-pipeline gate:", removal_gate(per_client))
print("\nbrownout (the moment a silent client surfaces BEFORE the hard stop):")
print("  v1 returns 410 for 1 hour -> nordwind-pipeline fails at 02:00, files a")
print("  ticket, migrates — weeks before the removal date instead of the morning after")
print("\n=> you cannot remove what you cannot measure (02.13): per-client usage,")
print("   verified technical contacts, brownouts — then the date.")
