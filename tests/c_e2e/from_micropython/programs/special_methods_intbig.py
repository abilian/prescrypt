# Test class special methods, that use a bigint.
from __future__ import annotations


class A:
    def __int__(self):
        return 1 << 100


print(int(A()))
