# converting user instance to buffer
from __future__ import annotations


class C:
    pass

c = C()
try:
    d = bytes(c)
except TypeError:
    print('TypeError')
