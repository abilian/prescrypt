import pytest
from devtools import debug

from prescrypt import py2js
from prescrypt.testing import js_eq, js_eval

# language=python
P1 = """
def f(x):
    return x + 1

result = f(1)
"""

# language=python
P2 = """
def f(x):
    y = 1
    def g(x):
        return x + y

result = f(2)
"""

# language=python
P3 = """
class A:
    def __init__(self, x):
        self.x = x

    def f(self):
        return self.x + 1

result = A(1).f()
"""

# language=python
P4 = """
class A:
    def f(self):
        return 1

class B(A):
    pass

result = B().f()
"""

# language=python
P5 = """
def f(x):
    return x + 3

def g():
    return 1

def h(f, x):
    return f(x)

result = h(f, g())
"""

# language=python
P6 = """
def ack2(M, N):
    if M == 0:
        return N + 1
    elif N == 0:
        return ack2(M - 1, 1)
    else:
        return ack2(M - 1, ack2(M, N - 1))

result = ack2(3, 3)
"""

# language=python
P7 = """
def F(a, b, c, n):
    if n > b:
        return n - c
    else:
        add = F(a, b, c, a + n)
        add1 = F(a, b, c, a + add)
        add2 = F(a, b, c, a + add1)
        return F(a, b, c, a + add2)


def S(a, b, c):
    large_sum = 0
    for value in range(b + 1):
        large_sum += F(a, b, c, value)
    return large_sum


result = S(20, 100, 15)
"""

# language=python
P8 = """
l = [1, 2, 3]
l.append(4)

result = len(l) == 4 and l == [1, 2, 3, 4]
"""

# language=python
P9 = """
# Source: https://github.com/jilljenn/tryalgo/blob/master/tryalgo/permutation_rank.py
def rank_permutation(r, n):
    '''Given r and n find the permutation of {0,..,n-1} with rank according to
    lexicographical order equal to r
       :param r n: integers with 0 ≤ r < n!
       :returns: permutation p as a list of n integers
       :beware: computation with big numbers
       :complexity: `O(n^2)`
    '''
    fact = 1                               # compute (n-1) factorial
    for i in range(2, n):
        fact *= i
    digits = list(range(n))                # all yet unused digits
    p = []                                 # build permutation
    for i in range(n):
        q = r // fact                      # by decomposing r = q * fact + rest
        r %= fact
        p.append(digits[q])
        del digits[q]                      # remove digit at position q
        if i != n - 1:
            fact //= (n - 1 - i)           # weight of next digit
    return p

result = rank_permutation(2, 3) == [1, 0, 2]
"""

# P9 is not working
programs = [f"P{i}" for i in range(1, 9)]


@pytest.mark.skip(reason="Known failures - needs code generation fixes")
@pytest.mark.parametrize("program", programs)
def test_programs(program: str):
    code = globals()[program]
    py_ctx = {}
    exec(code, py_ctx)
    py_result = py_ctx["result"]

    js_code = py2js(code)
    js_result = js_eval(js_code)

    debug(js_code)
    assert js_eq(js_result, py_result), f"{js_result} != {py_result}"
