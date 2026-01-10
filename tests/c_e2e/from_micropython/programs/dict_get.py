from __future__ import annotations

for d in {}, {42:2}:
    print(d.get(42))
    print(d.get(42,2))
