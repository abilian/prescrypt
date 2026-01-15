"""Tests for string and list method code generation."""

from __future__ import annotations

from prescrypt import py2js
from prescrypt.testing import js_eval


class TestStringMethods:
    """Test string methods."""

    def test_upper(self):
        assert js_eval(py2js("'hello'.upper()")) == "HELLO"

    def test_lower(self):
        assert js_eval(py2js("'HELLO'.lower()")) == "hello"

    def test_strip(self):
        assert js_eval(py2js("'  hello  '.strip()")) == "hello"

    def test_lstrip(self):
        assert js_eval(py2js("'  hello'.lstrip()")) == "hello"

    def test_rstrip(self):
        assert js_eval(py2js("'hello  '.rstrip()")) == "hello"

    def test_split(self):
        assert js_eval(py2js("'a,b,c'.split(',')")) == ["a", "b", "c"]

    def test_split_default(self):
        assert js_eval(py2js("'a b c'.split()")) == ["a", "b", "c"]

    def test_join(self):
        assert js_eval(py2js("','.join(['a', 'b', 'c'])")) == "a,b,c"

    def test_replace(self):
        assert js_eval(py2js("'hello'.replace('l', 'x')")) == "hexxo"

    def test_startswith(self):
        assert js_eval(py2js("'hello'.startswith('he')")) == True
        assert js_eval(py2js("'hello'.startswith('lo')")) == False

    def test_endswith(self):
        assert js_eval(py2js("'hello'.endswith('lo')")) == True
        assert js_eval(py2js("'hello'.endswith('he')")) == False

    def test_find(self):
        assert js_eval(py2js("'hello'.find('l')")) == 2
        assert js_eval(py2js("'hello'.find('x')")) == -1

    def test_index(self):
        assert js_eval(py2js("'hello'.index('l')")) == 2

    def test_count(self):
        assert js_eval(py2js("'hello'.count('l')")) == 2

    def test_isdigit(self):
        assert js_eval(py2js("'123'.isdigit()")) == True
        assert js_eval(py2js("'12a'.isdigit()")) == False

    def test_isalpha(self):
        assert js_eval(py2js("'abc'.isalpha()")) == True
        assert js_eval(py2js("'ab1'.isalpha()")) == False

    def test_isalnum(self):
        assert js_eval(py2js("'abc123'.isalnum()")) == True
        assert js_eval(py2js("'abc 123'.isalnum()")) == False

    def test_capitalize(self):
        assert js_eval(py2js("'hello'.capitalize()")) == "Hello"

    def test_title(self):
        assert js_eval(py2js("'hello world'.title()")) == "Hello World"

    def test_zfill(self):
        assert js_eval(py2js("'42'.zfill(5)")) == "00042"

    def test_center(self):
        result = js_eval(py2js("'hi'.center(6)"))
        assert len(result) == 6
        assert "hi" in result

    def test_ljust(self):
        result = js_eval(py2js("'hi'.ljust(5)"))
        assert len(result) == 5
        assert result.startswith("hi")

    def test_rjust(self):
        result = js_eval(py2js("'hi'.rjust(5)"))
        assert len(result) == 5
        assert result.endswith("hi")


class TestListMethods:
    """Test list methods."""

    def test_append(self):
        code = """
x = [1, 2]
x.append(3)
x
"""
        assert js_eval(py2js(code)) == [1, 2, 3]

    def test_extend(self):
        code = """
x = [1, 2]
x.extend([3, 4])
x
"""
        assert js_eval(py2js(code)) == [1, 2, 3, 4]

    def test_insert(self):
        code = """
x = [1, 3]
x.insert(1, 2)
x
"""
        assert js_eval(py2js(code)) == [1, 2, 3]

    def test_remove(self):
        code = """
x = [1, 2, 3, 2]
x.remove(2)
x
"""
        assert js_eval(py2js(code)) == [1, 3, 2]

    def test_pop(self):
        code = """
x = [1, 2, 3]
last = x.pop()
[x, last]
"""
        result = js_eval(py2js(code))
        assert result == [[1, 2], 3]

    def test_pop_index(self):
        code = """
x = [1, 2, 3]
first = x.pop(0)
[x, first]
"""
        result = js_eval(py2js(code))
        assert result == [[2, 3], 1]

    def test_index(self):
        assert js_eval(py2js("[1, 2, 3].index(2)")) == 1

    def test_count(self):
        assert js_eval(py2js("[1, 2, 2, 3].count(2)")) == 2

    def test_sort(self):
        code = """
x = [3, 1, 4, 1, 5]
x.sort()
x
"""
        assert js_eval(py2js(code)) == [1, 1, 3, 4, 5]

    def test_reverse(self):
        code = """
x = [1, 2, 3]
x.reverse()
x
"""
        assert js_eval(py2js(code)) == [3, 2, 1]

    def test_copy(self):
        code = """
x = [1, 2, 3]
y = x.copy()
x.append(4)
y
"""
        assert js_eval(py2js(code)) == [1, 2, 3]

    def test_clear(self):
        code = """
x = [1, 2, 3]
x.clear()
x
"""
        assert js_eval(py2js(code)) == []


class TestDictMethods:
    """Test dict methods."""

    def test_keys(self):
        code = """
d = {'a': 1, 'b': 2}
list(d.keys())
"""
        result = js_eval(py2js(code))
        assert set(result) == {"a", "b"}

    def test_values(self):
        code = """
d = {'a': 1, 'b': 2}
list(d.values())
"""
        result = js_eval(py2js(code))
        assert set(result) == {1, 2}

    def test_items(self):
        code = """
d = {'a': 1}
list(d.items())
"""
        assert js_eval(py2js(code)) == [["a", 1]]

    def test_get(self):
        assert js_eval(py2js("{'a': 1}.get('a')")) == 1
        assert js_eval(py2js("{'a': 1}.get('b')")) == None
        assert js_eval(py2js("{'a': 1}.get('b', 0)")) == 0

    def test_pop(self):
        code = """
d = {'a': 1, 'b': 2}
val = d.pop('a')
[val, d]
"""
        result = js_eval(py2js(code))
        assert result[0] == 1
        assert "a" not in result[1]

    def test_update(self):
        code = """
d = {'a': 1}
d.update({'b': 2})
d
"""
        result = js_eval(py2js(code))
        assert result == {"a": 1, "b": 2}


class TestMethodChaining:
    """Test method chaining."""

    def test_string_chain(self):
        assert js_eval(py2js("'  HELLO  '.strip().lower()")) == "hello"

    def test_list_chain(self):
        code = """
x = [3, 1, 2]
x.sort()
x.reverse()
x
"""
        assert js_eval(py2js(code)) == [3, 2, 1]
