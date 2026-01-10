# Exception chaining is not supported, but check that basic
# exception works as expected.
from __future__ import annotations

try:
    raise Exception from None
except Exception:
    print("Caught Exception")
