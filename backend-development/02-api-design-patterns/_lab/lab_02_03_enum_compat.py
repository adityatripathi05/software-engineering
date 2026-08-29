"""Lab for 02.3 API versioning.

Reproduces the incident with real validators standing in for generated SDKs: a
strict client (closed Literal — what Java/Go codegen produces) crashes on a new
enum value the server considers "additive"; a tolerant Python client shrugs.
"Additive" must be judged against your STRICTEST consumer.
"""
from typing import Literal

from pydantic import BaseModel, ValidationError


class InvoiceStrictSDK(BaseModel):
    """What a generated Java/Go SDK compiles: the enum is CLOSED."""
    id: str
    status: Literal["draft", "sent", "paid", "void"]


class InvoiceTolerantClient(BaseModel):
    """A duck-typed client: status is just a string it forwards."""
    id: str
    status: str


old_payload = {"id": "inv_9f2c41", "status": "paid"}
new_payload = {"id": "inv_9f2c41", "status": "partially_paid"}   # Tuesday's feature

print("before the release:")
print("  strict SDK  :", InvoiceStrictSDK.model_validate(old_payload).status)
print("  tolerant    :", InvoiceTolerantClient.model_validate(old_payload).status)

print("\nafter partial payments ship (server calls it additive):")
try:
    InvoiceStrictSDK.model_validate(new_payload)
except ValidationError as e:
    err = e.errors()[0]
    print(f"  strict SDK  : ValidationError {err['type']} — expected one of "
          f"{err['ctx']['expected']}")
print("  tolerant    :", InvoiceTolerantClient.model_validate(new_payload).status)

print("\n=> the same response is fine for one consumer and a crash for another —")
print("   on an invoice that was never partially paid, because DESERIALISATION")
print("   happens before any business logic (02.3). Enums ship open unless")
print("   deliberately closed, and CI round-trips new schemas through the")
print("   strictest generated SDK.")
