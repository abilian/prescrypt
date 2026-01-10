# test errors from bad operations with literals
# these raise a SyntaxWarning in CPython; see https://bugs.python.org/issue15248

# unsupported subscription
from __future__ import annotations

try:
    1[0]
except TypeError:
    print("TypeError")
try:
    ""[""]
except TypeError:
    print("TypeError")

# not callable
try:
    1()
except TypeError:
    print("TypeError")
