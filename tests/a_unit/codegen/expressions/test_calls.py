from __future__ import annotations

import pytest

from prescrypt.codegen import CodeGen
from prescrypt.codegen._expressions.calls import FuncCall
from prescrypt.front import ast

from .utils import check_gen

FUNC_CALLS = [
    # Calls to user-defined functions
    ("f()", "f()"),
    ("f(1, 2)", "f(1, 2)"),
    ("f(1, 2, 3)", "f(1, 2, 3)"),
    ("f(a=1)", "f({flx_args: [], flx_kwargs: {a: 1}})"),
    ("f(1, a=1)", "f({flx_args: [1], flx_kwargs: {a: 1}})"),
    ("f(1, 2, a=1)", "f({flx_args: [1, 2], flx_kwargs: {a: 1}})"),
    # ("f(*t)", ""), # TODO
    ("f(*t, a=1)", "f({flx_args: t, flx_kwargs: {a: 1}})"),
    ("f(*t, **kw)", "f({flx_args: t, flx_kwargs: kw})"),
    # Calls to stdlib functions - optimized for primitive types
    ("print(1)", "console.log(1)"),  # Int is primitive, no str() needed
    ("str(1)", "String(1)"),  # Int uses String() constructor
    ("bool(1)", "!!(_pyfunc_truthy(1))"),
    ("round(1)", "_pyfunc_round(1)"),
    # Calls to methods
    ("a.b()", "a.b()"),
    ("a.b(1)", "a.b(1)"),
    ("a.b(1, 2)", "a.b(1, 2)"),
    ("a.b(1, a=2, b=3)", "a.b({flx_args: [1], flx_kwargs: {a: 2, b: 3}})"),
    ("a.b(*t, **kw)", "a.b({flx_args: t, flx_kwargs: kw})"),
    # Calls to builtin methods (JS)
    ("'a'.lower()", "_pymeth_lower.call('a')"),
    # Calls to builtin methods (PY)
    # FIXME: ("[1,2,3].sort()", "_pymeth_sort.call([1, 2, 3])"),
    # FIXME: ("'{a}'.format(a=1)", "_pymeth_format.call('{a}', {a: 1})"),
]


@pytest.mark.parametrize(("code", "expected"), FUNC_CALLS)
def test_func_call(code, expected):
    module = ast.parse(code)
    codegen = CodeGen(module)
    call_node = module.body[0].value
    func_call = FuncCall(call_node, codegen)
    assert func_call.gen() == expected


@pytest.mark.parametrize(("code", "expected"), FUNC_CALLS)
def test_func_call_2(code, expected):
    check_gen(code, expected)
