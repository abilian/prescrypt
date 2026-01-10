# test passing named arg to closed-over function
from __future__ import annotations


def f():
    x = 1
    def g(z):
        print(x, z)
    return g

f()(z=42)
