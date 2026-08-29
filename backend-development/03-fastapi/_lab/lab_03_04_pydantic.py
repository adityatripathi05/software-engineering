"""Lab for 03.4 Pydantic v2 in depth.

Reproduces the money captures: lax coercion silently admitting numeric strings
into float (with binary float error), strict mode refusing, and Decimal carrying
the amount exactly — the mechanism behind the VAT incident.
"""
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, ValidationError


class LaxLine(BaseModel):
    amount: float


class StrictLine(BaseModel):
    model_config = ConfigDict(strict=True)
    amount: float


class MoneyLine(BaseModel):
    amount: Decimal


print("lax float from CSV string '19.99':", LaxLine(amount="19.99").amount)
print("binary float arithmetic: 0.1 + 0.2 =", 0.1 + 0.2)
print("sum of 10 x '19.99' as float:", sum(LaxLine(amount="19.99").amount for _ in range(10)))
print("sum of 10 x '19.99' as Decimal:", sum(MoneyLine(amount="19.99").amount for _ in range(10)))

try:
    StrictLine(amount="19.99")
except ValidationError as e:
    print("\nstrict=True vs the same string ->", e.errors()[0]["type"])

print("\nDecimal survives exactly:", MoneyLine(amount="19.99").amount,
      "| model_dump(mode='json'):", MoneyLine(amount="19.99").model_dump(mode="json"))
