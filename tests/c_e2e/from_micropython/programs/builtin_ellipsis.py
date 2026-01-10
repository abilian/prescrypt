# tests that .../Ellipsis exists
from __future__ import annotations

print(...)
print(Ellipsis)

print(... == Ellipsis)

# Test that Ellipsis can be hashed
print(type(hash(Ellipsis)))
