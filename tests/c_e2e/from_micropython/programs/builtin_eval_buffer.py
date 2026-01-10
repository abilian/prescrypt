# test builtin eval with a buffer (bytearray/memoryview) input
from __future__ import annotations

try:
    eval
    bytearray
    memoryview
except:
    print("SKIP")
    raise SystemExit

print(eval(bytearray(b'1 + 1')))
print(eval(memoryview(b'2 + 2')))
