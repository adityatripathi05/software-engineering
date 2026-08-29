"""Lab for 02.7 Bulk operations and partial updates.

Reproduces the field-erasing PATCH: `model_dump()` materialises EVERY field —
absent ones as null — so a one-field update nulls three others under 200 OK.
`model_dump(exclude_unset=True)` preserves the three-state distinction:
absent (don't touch) · null (clear it) · valued (set it).
"""
from datetime import date

from pydantic import BaseModel


class InvoicePatch(BaseModel):
    due_date: date | None = None
    po_number: str | None = None
    notes: str | None = None
    contact_email: str | None = None


STORED = {"due_date": "2026-10-15", "po_number": "PO-4471",
          "notes": "net-30 agreed", "contact_email": "ap@nordwind.example"}

patch = InvoicePatch.model_validate({"due_date": "2026-10-31"})   # the whole request

naive = {**STORED, **{k: v for k, v in patch.model_dump(mode="json").items()}}
correct = {**STORED, **patch.model_dump(mode="json", exclude_unset=True)}

print("client sent ONLY: {'due_date': '2026-10-31'}\n")
print("naive  model_dump()                :", patch.model_dump(mode="json"))
print("  -> stored row afterwards         :", naive)
print("  => po_number, notes, contact_email erased; the response was 200 OK\n")
print("model_dump(exclude_unset=True)     :", patch.model_dump(mode="json", exclude_unset=True))
print("  -> stored row afterwards         :", correct)

explicit_clear = InvoicePatch.model_validate({"po_number": None})
print("\nexplicit clear {'po_number': null} :",
      explicit_clear.model_dump(mode="json", exclude_unset=True))
print("=> three states, all distinguishable: absent = don't touch; null = clear;")
print("   valued = set. Collapsing absent into null is the incident (02.7).")
