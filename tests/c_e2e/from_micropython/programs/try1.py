# basic exceptions
from __future__ import annotations

x = 1
try:
    x.a()
except:
    print(x)

try:
    raise IndexError
except IndexError:
    print("caught")
