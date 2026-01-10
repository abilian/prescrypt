# test closure with default args
from __future__ import annotations


def f():
    a = 1
    def bar(b = 10, c = 20):
        print(a + b + c)
    bar()
    bar(2)
    bar(2, 3)

print(f())
