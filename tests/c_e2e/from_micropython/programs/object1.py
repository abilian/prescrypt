# test builtin object()

# creation
from __future__ import annotations

object()

# printing
print(repr(object())[:7])
