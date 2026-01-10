# uPy behaviour only: builtin modules are read-only
from __future__ import annotations

import sys

try:
    sys.x = 1
except AttributeError:
    print("AttributeError")
