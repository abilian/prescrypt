# calling a function from a function
from __future__ import annotations


def f(x):
    print(x + 1)

def g(x):
    f(2 * x)
    f(4 * x)

g(3)
