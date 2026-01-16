"""Tests for annotated assignment (AnnAssign)."""

from __future__ import annotations

from prescrypt import py2js


def js(code: str) -> str:
    """Compile Python to JavaScript without stdlib."""
    return py2js(code, include_stdlib=False)


class TestAnnAssignBasic:
    """Basic annotated assignment tests."""

    def test_annassign_int(self):
        """Annotated assignment with int."""
        code = "x: int = 5"
        result = js(code)
        assert "const x = 5" in result

    def test_annassign_str(self):
        """Annotated assignment with str."""
        code = 'name: str = "Alice"'
        result = js(code)
        assert "const name = 'Alice'" in result

    def test_annassign_bool(self):
        """Annotated assignment with bool."""
        code = "active: bool = True"
        result = js(code)
        assert "const active = true" in result

    def test_annassign_float(self):
        """Annotated assignment with float."""
        code = "price: float = 19.99"
        result = js(code)
        assert "const price = 19.99" in result

    def test_annassign_list(self):
        """Annotated assignment with list."""
        code = "items: list = [1, 2, 3]"
        result = js(code)
        assert "const items = [1, 2, 3]" in result


class TestAnnAssignDeclarationOnly:
    """Tests for declaration-only annotations."""

    def test_declaration_only(self):
        """Declaration without value."""
        code = """
x: int
x = 10
"""
        result = js(code)
        assert "let x;" in result
        assert "x = 10" in result

    def test_multiple_declarations(self):
        """Multiple declaration-only annotations."""
        code = """
a: int
b: str
a = 1
b = "hello"
"""
        result = js(code)
        assert "let a;" in result
        assert "let b;" in result


class TestAnnAssignInFunction:
    """Tests for annotated assignment in functions."""

    def test_in_function(self):
        """Annotated assignment inside function."""
        code = """
def foo():
    result: int = 0
    return result
"""
        result = js(code)
        assert "const result = 0" in result

    def test_function_with_typed_params(self):
        """Function with typed parameters and local vars."""
        code = """
def add(a: int, b: int) -> int:
    result: int = a + b
    return result
"""
        result = js(code)
        assert "const result" in result


class TestAnnAssignComplex:
    """Tests for complex annotation scenarios."""

    def test_complex_annotation(self):
        """Complex type annotations are handled."""
        code = 'data: dict = {"a": 1}'
        result = js(code)
        assert "const data" in result
        # Dict literals are compiled to _pyfunc_create_dict calls
        assert "_pyfunc_create_dict('a', 1)" in result or '"a": 1' in result

    def test_annotation_with_expression(self):
        """Annotation with computed value."""
        code = """x: int = 1 + 2"""
        result = js(code)
        # May be constant-folded to 3
        assert "x = 3" in result or "x = (1 + 2)" in result
