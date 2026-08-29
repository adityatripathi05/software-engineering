"""Lab for 02.12 Rate limiting as an API contract.

Reproduces the month-end lockout with a real token bucket: one shared bucket
per tenant lets the overnight sync drain it and 429 twelve humans; quota
classes derived from the credential type give each kind of traffic its own
fate. Every 200 carries RateLimit-*; every 429 carries Retry-After.
"""
import time


class TokenBucket:
    def __init__(self, capacity: int, refill_per_s: float):
        self.capacity, self.refill = capacity, refill_per_s
        self.tokens, self.at = float(capacity), time.monotonic()

    def take(self) -> tuple[bool, dict[str, str]]:
        now = time.monotonic()
        self.tokens = min(self.capacity, self.tokens + (now - self.at) * self.refill)
        self.at = now
        headers = {"RateLimit-Limit": str(self.capacity),
                   "RateLimit-Remaining": str(max(0, int(self.tokens) - 1))}
        if self.tokens >= 1:
            self.tokens -= 1
            return True, headers
        headers["Retry-After"] = str(max(1, int((1 - self.tokens) / self.refill)))
        return False, headers


def month_end(buckets: dict[str, TokenBucket], label: str) -> None:
    batch_bucket = buckets["batch"]
    for _ in range(60):                          # the overnight sync, bursting
        batch_bucket.take()
    ok, headers = buckets["dashboard"].take()    # 00:12 — a human loads a page
    print(f"{label}:")
    print(f"  after 60 batch calls, a dashboard request -> "
          f"{'200 OK' if ok else '429 Too Many Requests'}   {headers}")


shared = TokenBucket(capacity=50, refill_per_s=1)
month_end({"batch": shared, "dashboard": shared}, "ONE shared bucket per tenant")

month_end({"batch": TokenBucket(40, 1), "dashboard": TokenBucket(10, 1)},
          "quota classes by credential type (api-key vs session)")

print("\n=> whoever shares a bucket shares a fate (02.12): the class derives from")
print("   the credential, RateLimit-* rides every 200 so clients pace BEFORE the")
print("   429, and Retry-After (01.3) tells the batch exactly when to resume.")
