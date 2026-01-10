# test subclassing a native type which can be iterated over
from __future__ import annotations


class mymap(map):
    pass

m = mymap(lambda x: x + 10, range(4))
print(list(m))
