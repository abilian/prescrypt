# test using the name "super" as a local variable
from __future__ import annotations


class A:
    def foo(self):
        super = [1, 2]
        super.pop()
        print(super)

A().foo()
