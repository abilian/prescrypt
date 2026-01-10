from __future__ import annotations

import pytest

from .utils import check_gen

OPS = [
    # Int
    ("1 + 1", "_pyfunc_op_add(1, 1)"),
    ("1 - 1", "1 - 1"),
    ("1 * 1", "_pyfunc_op_mul(1, 1)"),
    ("1 / 1", "1 / 1"),
    ("1 // 1", "Math.floor(1/1)"),
    ("1 % 1", "1 % 1"),
    ("1 ** 1", "Math.pow(1, 1)"),
    ("1 << 1", "1 << 1"),
    ("1 >> 1", "1 >> 1"),
    ("1 & 1", "1 & 1"),
    ("1 | 1", "1 | 1"),
    ("1 ^ 1", "1 ^ 1"),
    ("~1", "~1"),
    # Bool
    ("True and True", "true && true"),
    ("True or True", "true || true"),
    ("not True", "!true"),
    # Float
    ("1.0 + 1.0", "_pyfunc_op_add(1.0, 1.0)"),
    ("1.0 - 1.0", "1.0 - 1.0"),
    ("1.0 * 1.0", "_pyfunc_op_mul(1.0, 1.0)"),
    # Strings
    ("'a' + 'b'", "_pyfunc_op_add('a', 'b')"),
    ("'a' * 2", "_pyfunc_op_mul('a', 2)"),
    # Lists
    ("[1] + [2]", "_pyfunc_op_add([1], [2])"),
    ("[1] * 2", "_pyfunc_op_mul([1], 2)"),
    # Tuples
    ("(1,) + (2,)", "_pyfunc_op_add([1], [2])"),
    ("(1,) * 2", "_pyfunc_op_mul([1], 2)"),
    # Dicts
    ("{} + {}", "_pyfunc_op_add(_pyfunc_create_dict(), _pyfunc_create_dict())"),
    # Comparisons
    ("1 == 1", "_pyfunc_op_equals(1, 1)"),
    ("1 != 1", "!_pyfunc_op_equals(1, 1)"),
    ("1 < 1", "1 < 1"),
    ("1 <= 1", "1 <= 1"),
    ("1 > 1", "1 > 1"),
    ("1 >= 1", "1 >= 1"),
    ("1 in [1]", "_pyfunc_op_contains(1, [1])"),
    ("1 not in [1]", "!_pyfunc_op_contains(1, [1])"),
    ("1 is 1", "1 === 1"),
    ("1 is not 1", "1 !== 1"),
    ("1 < 1 < 1", "(1 < 1) && (1 < 1)"),
    ("1 < 1 > 1", "(1 < 1) && (1 > 1)"),
    ("1 < 1 <= 1", "(1 < 1) && (1 <= 1)"),
    ("1 < 1 >= 1", "(1 < 1) && (1 >= 1)"),
    ("1 < 1 == 1", "(1 < 1) && _pyfunc_op_equals(1, 1)"),
    # Other ops
    ("a[1]", "a[1]"),
    ("a.b", "a.b"),
    # FIXME("a.b.c", "a.b.c"),
    # Misc
    # FIXME: ("'%s' % 1", "_pyfunc_op_mod('%s', 1)"),
]


@pytest.mark.parametrize("code,expected", OPS)
def test_ops(code, expected):
    check_gen(code, expected)
