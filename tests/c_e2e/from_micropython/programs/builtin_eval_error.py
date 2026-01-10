# test if eval raises SyntaxError
from __future__ import annotations

try:
    eval
except NameError:
    print("SKIP")
    raise SystemExit

try:
    print(eval("[1,,]"))
except SyntaxError:
    print("SyntaxError")
