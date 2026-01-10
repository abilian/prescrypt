from __future__ import annotations

try:
    1 // 0
except ZeroDivisionError:
    print("ZeroDivisionError")

try:
    1 % 0
except ZeroDivisionError:
    print("ZeroDivisionError")
