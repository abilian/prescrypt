# test bad exception match
from __future__ import annotations

try:
    try:
        a
    except 1:
        pass
except TypeError:
    print("TypeError")

try:
    try:
        a
    except (1,):
        pass
except TypeError:
    print("TypeError")
