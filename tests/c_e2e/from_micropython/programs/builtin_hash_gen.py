# test builtin hash function, on generators
from __future__ import annotations


def gen():
    yield

print(type(hash(gen)))
print(type(hash(gen())))
