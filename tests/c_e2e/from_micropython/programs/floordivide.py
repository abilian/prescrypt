# check modulo matches python definition

# This tests compiler version
from __future__ import annotations

print(123 // 7)
print(-123 // 7)
print(123 // -7)
print(-123 // -7)

a = 10000001
b = 10000000
print(a // b)
print(a // -b)
print(-a // b)
print(-a // -b)
