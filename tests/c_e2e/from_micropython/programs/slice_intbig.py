# test slicing when arguments are bignums
from __future__ import annotations

print(list(range(10))[(1<<66)>>65:])
print(list(range(10))[:(1<<66)>>65])
print(list(range(10))[::(1<<66)>>65])
