# MicroPython doesn't support tuple argument
from __future__ import annotations

try:
    "foobar".endswith(("bar", "sth"))
except TypeError:
    print("TypeError")
