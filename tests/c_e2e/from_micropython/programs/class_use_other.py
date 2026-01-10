# check that we can use an instance of B in a method of A
from __future__ import annotations


class A:
    def store(a, b):
        a.value = b

class B:
    pass

b = B()
A.store(b, 1)
print(b.value)
