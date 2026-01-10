# test returning from within a for loop
from __future__ import annotations


def f():
    for i in [1, 2, 3]:
        return i

print(f())
