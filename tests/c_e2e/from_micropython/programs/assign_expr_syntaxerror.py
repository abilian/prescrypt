# test SyntaxError with := operator
from __future__ import annotations


def test(code):
    try:
        print(eval(code))
    except SyntaxError:
        print('SyntaxError')

test("x := 1")
test("((x, y) := 1)")
test("([i := i + 1 for i in range(4)])")
test("([i := -1 for i, j in [(1, 2)]])")
test("([[(i := j) for i in range(2)] for j in range(2)])")

# this is currently allowed in MicroPython, but not in CPython
test("([[(j := i) for i in range(2)] for j in range(2)])")
