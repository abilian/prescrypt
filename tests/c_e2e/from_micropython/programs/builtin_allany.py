# test builtin "all" and "any"
from __future__ import annotations

tests = (
    (),
    [],
    [False],
    [True],
    [False, True],
    [True, False],
    [False, False],
    [True, True],
    range(10),
)

for test in tests:
    print(all(test))

for test in tests:
    print(any(test))
