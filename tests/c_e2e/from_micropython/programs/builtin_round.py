# test round() with integral values
from __future__ import annotations

tests = [
    False, True,
    0, 1, -1, 10
]
for t in tests:
    print(round(t))
