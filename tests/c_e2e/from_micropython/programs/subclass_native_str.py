# Test subclassing built-in str
from __future__ import annotations


class S(str):
    pass

s = S('hello')
print(s == 'hello')
print('hello' == s)
print(s == 'Hello')
print('Hello' == s)
