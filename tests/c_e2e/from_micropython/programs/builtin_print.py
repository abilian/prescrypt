# test builtin print function
from __future__ import annotations

print()
print(None)
print('')
print(1)
print(1, 2)

print(sep='')
print(sep='x')
print(end='')
print(end='x\n')
print(1, sep='')
print(1, end='')
print(1, sep='', end='')
print(1, 2, sep='')
print(1, 2, end='')
print(1, 2, sep='', end='')

print([{1:2}])
