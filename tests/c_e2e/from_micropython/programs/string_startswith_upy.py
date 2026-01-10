# MicroPython doesn't support tuple argument
from __future__ import annotations

try:
    "foobar".startswith(("foo", "sth"))
except TypeError:
    print("TypeError")
