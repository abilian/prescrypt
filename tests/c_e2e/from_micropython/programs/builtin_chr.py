# test builtin chr (whether or not we support unicode)
from __future__ import annotations

print(chr(65))

try:
    chr(0x110000)
except ValueError:
    print("ValueError")
