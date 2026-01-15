from __future__ import annotations

from .utils import check_gen_exec


class TestForLoop:
    """Test for loop code generation."""

    def test_for_range(self):
        """Test for loop with range()."""
        code = """
result = 0
for i in range(5):
    result = result + i
result
"""
        check_gen_exec(code, 10)

    def test_for_list(self):
        """Test for loop over a list."""
        code = """
items = [10, 20, 30]
result = 0
for x in items:
    result = result + x
result
"""
        check_gen_exec(code, 60)

    def test_for_enumerate(self):
        """Test for loop with enumerate()."""
        code = """
items = [10, 20, 30]
result = 0
for i, x in enumerate(items):
    result = result + i + x
result
"""
        check_gen_exec(code, 63)

    def test_for_tuple_unpacking(self):
        """Test for loop with tuple unpacking."""
        code = """
pairs = [(1, 2), (3, 4)]
result = 0
for a, b in pairs:
    result = result + a + b
result
"""
        check_gen_exec(code, 10)

    def test_for_else_no_break(self):
        """Test for-else without break (else should run)."""
        code = """
result = 'not found'
for i in range(3):
    pass
else:
    result = 'completed'
result
"""
        check_gen_exec(code, "completed")

    def test_for_else_with_break(self):
        """Test for-else with break (else should not run)."""
        code = """
result = 'not found'
for i in range(5):
    if i == 3:
        result = 'found at 3'
        break
else:
    result = 'completed'
result
"""
        check_gen_exec(code, "found at 3")

    def test_for_else_no_match(self):
        """Test for-else without matching condition (else should run)."""
        code = """
result = 'not found'
for i in range(3):
    if i == 10:
        result = 'found at 10'
        break
else:
    result = 'completed'
result
"""
        check_gen_exec(code, "completed")


class TestWhileLoop:
    """Test while loop code generation."""

    def test_while_basic(self):
        """Test basic while loop."""
        code = """
result = 0
i = 0
while i < 5:
    result = result + i
    i = i + 1
result
"""
        check_gen_exec(code, 10)

    def test_while_with_break(self):
        """Test while loop with break."""
        code = """
result = 0
i = 0
while i < 10:
    if i == 5:
        break
    result = result + i
    i = i + 1
result
"""
        check_gen_exec(code, 10)

    def test_while_with_continue(self):
        """Test while loop with continue."""
        code = """
result = 0
i = 0
while i < 5:
    i = i + 1
    if i == 3:
        continue
    result = result + i
result
"""
        check_gen_exec(code, 12)  # 1 + 2 + 4 + 5 = 12


class TestGlobalNonlocal:
    """Test global and nonlocal statement handling."""

    def test_global_variable(self):
        """Test global variable modification."""
        code = """
x = 1

def foo():
    global x
    x = 2

foo()
x
"""
        check_gen_exec(code, 2)

    def test_nonlocal_variable(self):
        """Test nonlocal variable modification."""
        code = """
def outer():
    x = 1
    def inner():
        nonlocal x
        x = 2
    inner()
    return x

result = outer()
result
"""
        check_gen_exec(code, 2)

    def test_global_creates_let(self):
        """Test that global declaration makes outer variable use 'let' not 'const'."""
        code = """
x = 1

def foo():
    global x
    x = 2
"""
        from prescrypt import py2js
        js = py2js(code)
        # x should be 'let' not 'const' because it's modified via global
        assert "let x = 1;" in js

    def test_nonlocal_creates_let(self):
        """Test that nonlocal declaration makes enclosing variable use 'let'."""
        code = """
def outer():
    x = 1
    def inner():
        nonlocal x
        x = 2
    inner()
    return x
"""
        from prescrypt import py2js
        js = py2js(code)
        # x should be 'let' not 'const' in outer because it's modified via nonlocal
        assert "let x = 1;" in js


class TestWithStatement:
    """Test with statement code generation."""

    def test_with_binding(self):
        """Test with statement with 'as' binding."""
        code = """
class MockContext:
    def __init__(self, value):
        self.value = value
        self.closed = False
    def close(self):
        self.closed = True

ctx = MockContext(42)
with ctx as c:
    result = c.value
result
"""
        # Note: This test just verifies code generation works.
        # Full semantics would require __enter__/__exit__ support.
        from prescrypt import py2js
        js = py2js(code)
        assert "try {" in js
        assert "finally {" in js
        assert "close" in js

    def test_with_no_binding(self):
        """Test with statement without 'as' binding."""
        code = """
class MockLock:
    def close(self):
        pass

lock = MockLock()
with lock:
    result = 1
result
"""
        from prescrypt import py2js
        js = py2js(code)
        assert "try {" in js
        assert "finally {" in js


class TestIfStatement:
    """Test if statement code generation."""

    def test_if_basic(self):
        """Test basic if statement."""
        code = """
result = 0
if True:
    result = 1
result
"""
        check_gen_exec(code, 1)

    def test_if_else(self):
        """Test if-else statement."""
        code = """
x = 5
result = ''
if x > 3:
    result = 'big'
else:
    result = 'small'
result
"""
        check_gen_exec(code, "big")

    def test_if_elif_else(self):
        """Test if-elif-else statement."""
        code = """
x = 5
if x < 3:
    result = 'small'
elif x < 7:
    result = 'medium'
else:
    result = 'big'
result
"""
        check_gen_exec(code, "medium")
