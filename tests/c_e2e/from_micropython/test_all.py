from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from prescrypt.compiler import py2js

PROGRAMS_DIR = Path(__file__).parent / "programs"

DENY_LIST = {
    # Hangs the program
    "string_format2.py",
    # Not implemented (yet?)
    "assign1.py", # Multiple assignment not (yet) supported.
    "assign_expr.py", # gen_expr not implemented for <NamedExpr (AST node)>
    "assign_expr_scope.py", #] - SyntaxError: no binding for nonlocal 'var5' found
    "builtin_callable.py", # gen_expr not implemented for <Lambda (AST node)>
    "builtin_dir.py", # Multiple inheritance not (yet) supported.
    "builtin_ellipsis.py", #] - ValueError: Unknown type: <class 'ellipsis'>
    "builtin_getattr.py", # gen_call not implemented for <Call (AST node)>
    "builtin_hash_gen.py", # gen_expr not implemented for <Yield (AST node)>
    "builtin_id.py", # gen_expr not implemented for <Lambda (AST node)>
    "builtin_map.py", # gen_expr not implemented for <Lambda (AST node)>
    "builtin_slice.py", # gen_expr not implemented for <Slice (AST node)>
    "builtin_str_hex.py", #] - ValueError: Unknown type: <class 'bytes'>
    "class_bases.py", # Multiple inheritance not (yet) supported.
    "class_bind_self.py", # gen_expr not implemented for <Lambda (AST node)>
    "class_getattr.py", # gen_expr not implemented for <Lambda (AST node)>
    "class_inherit_mul.py", # Multiple inheritance not (yet) supported.
    "class_instance_override.py", # gen_expr not implemented for <Lambda (AST node)>
    "class_super_aslocal.py", #] - ValueError: cannot assign to 'super'
    "class_super_multinherit.py", # Multiple inheritance not (yet) supported.
    "closure1.py", # gen_call not implemented for <Call (AST node)>
    "closure2.py", # gen_call not implemented for <Call (AST node)>
    "closure_manyvars.py", # gen_assign not implemented for <Assign (AST node)>
    "closure_namedarg.py", # gen_call not implemented for <Call (AST node)>
    "comprehension1.py", # gen_expr not implemented for <DictComp (AST node)>
    "decorator.py", # gen_expr not implemented for <Lambda (AST node)>
    "dict_construct.py", # dict() takes at most one argument
    "dict_copy.py", # gen_expr not implemented for <DictComp (AST node)>
    "fun_kwonlydef.py", #] - AttributeError: module 'prescrypt.front.ast.ast' has no attribute 'NoneType'
    "fun_str.py", # gen_expr not implemented for <Slice (AST node)>
    "gen_yield_from.py", # gen_expr not implemented for <Yield (AST node)>
    "gen_yield_from_iter.py", # gen_expr not implemented for <YieldFrom (AST node)>
    "generator1.py", # gen_expr not implemented for <Yield (AST node)>
    "generator2.py", # gen_expr not implemented for <GeneratorExp (AST node)>
    "generator_args.py", # gen_expr not implemented for <Yield (AST node)>
    "generator_closure.py", # gen_expr not implemented for <Yield (AST node)>
    "globals_del.py", # gen_expr not implemented for <Lambda (AST node)>
    "lambda1.py", # gen_expr not implemented for <Lambda (AST node)>
    "lambda_defargs.py", # gen_expr not implemented for <Lambda (AST node)>
    "list_slice_3arg.py", # gen_expr not implemented for <Slice (AST node)>
    "list_slice_assign_grow.py", # gen_expr not implemented for <Slice (AST node)>
    "list_sort.py", # gen_expr not implemented for <Lambda (AST node)>
    "object1.py", # gen_expr not implemented for <Slice (AST node)>
    "scope.py", # gen_call not implemented for <Call (AST node)>
    "scope_class.py", # gen_expr not implemented for <Lambda (AST node)>
    "slice_intbig.py", # gen_expr not implemented for <Slice (AST node)>
    "string_format.py", # gen_expr not implemented for <Starred (AST node)>
    "string_format_cp310.py", # gen_expr not implemented for <Starred (AST node)>
    "string_fstring_debug.py", # gen_assign not implemented for <Assign (AST node)>
    "string_slice.py", #] - ValueError: Unknown type: <class 'bytes'>
    "subclass_native2_list.py", # Multiple inheritance not (yet) supported.
    "subclass_native2_tuple.py", # Multiple inheritance not (yet) supported.
    "subclass_native5.py", # Multiple inheritance not (yet) supported.
    "subclass_native_containment.py", #] - ValueError: Unknown type: <class 'bytes'>
    "subclass_native_init.py", # Multiple inheritance not (yet) supported.
    "subclass_native_iter.py", # gen_expr not implemented for <Lambda (AST node)>
    "tuple_slice.py", # gen_expr not implemented for <Slice (AST node)>
    # Node failure
    "builtin_bin.py", # Node failed
    "builtin_bin_intbig.py", # Node failed
    "builtin_hash_intbig.py", # Node failed
    "builtin_hex.py", # Node failed
    "builtin_hex_intbig.py", # Node failed
    "builtin_len1.py", # Node failed
    "builtin_locals.py", # Node failed
    "builtin_oct.py", # Node failed
    "builtin_oct_intbig.py", # Node failed
    "class1.py", # Node failed
    "class3.py", # Node failed
    "class_contains.py", # Node failed
    "class_dict.py", # Node failed
    "class_inherit1.py", # Node failed
    "class_use_other.py", # Node failed
    "dict2.py", # Node failed
    "dict_del.py", # Node failed
    "dict_fromkeys.py", # Node failed
    "dict_specialmeth.py", # Node failed
    "dict_update.py", # Node failed
    "equal.py", # Node failed
    "exception1.py", # Node failed
    "fun_calldblstar3.py", # Node failed
    "fun_callstar.py", # Node failed
    "fun_kwvarargs.py", # Node failed
    "fun_varargs.py", # Node failed
    "ifcond.py", # Node failed
    "iter2.py", # Node failed
    "iter_of_iter.py", # Node failed
    "list_copy.py", # Node failed
    "list_extend.py", # Node failed
    "module1.py", # Node failed
    "module_dict.py", # Node failed
    "object_dict.py", # Node failed
    "string_compare.py", # Node failed
    "string_mult.py", # Node failed
    "subclass_native4.py", # Node failed
    "subclass_native_buffer.py", # Node failed
    "subclass_native_cmp.py", # Node failed
    "subclass_native_specmeth.py", # Node failed
    "subclass_native_str.py", # Node failed
    "sys_path.py", # Node failed
    "types2.py", # Node failed
    "unary_op.py", # Node failed
    # Other failures
    "andor.py", # assert '1\n[1]\nfalse\n1' == '1\n(1,)\n()\n1'
    "builtin_abs_intbig.py", # assert '1.2345678901...0368744177664' == '123456789012...0368744177664'
    "builtin_allany.py", # assert 'true\ntrue\n...e\ntrue\ntrue' == 'True\nTrue\n...e\nTrue\nTrue'
    "builtin_print.py", # 1\n1...12\n[{"1":2}]' == 'None\n\n1\n1...1 212[{1: 2}]'
    "builtin_sum.py", # assert '0\n0\n0\n0\n...n3\n3\n45\n45' == '0\n-2\n0\n-2...n3\n1\n45\n43'
    "class_binop.py", # assert 'eq\ntrue\nfa...e\ntrue\ntrue' == 'eq\nTrue\nlt...rue\nge\nTrue'
    "class_inplace_op.py", # Obje...\n{"v":[1,2]}' == 'A(8)\nA(5)\n...[1, 2, 3, 4])'
    "class_number.py", # assert '' == '0 + 1\n0 - 2'
    "class_reverse_op.py", # assert '[object Obje...]\nnull\nnull' == 'A(4)\nA(7)\n...(a*b)\nB(a/b)'
    "class_staticclassmethod.py", # assert 'f 0\ng \nsta...nstatic get 3' == 'f 0\ng 0\nsu...nstatic del 3'
    "class_store.py", # assert '1\n1 \n2 3\n \n\n4' == '1\n1 3\n2 3\n2 3\n2\n4'
    "class_str.py", # :1}\...\n{"value":1}' == 'str<C1 1>\nr...2>\nstr<C3 1>'
    "closure_defargs.py", # assert 'null\nnull\n6' == '31\n23\n6\nNone'
    "compare_multi.py", # assert 'true\ntrue\nfalse\nfalse' == 'True\nTrue\nFalse\nFalse'
    "del_subscr.py", # ]\n[...{"0":{"0":0}}' == '[1, 2, 3]\n[...\n{}\n{0: {}}'
    "dict_clear.py", # "2":42}' == '2\n{}\n{2: 42}'
    "dict_get.py", # assert 'null\n2\n2\n2' == 'None\n2\n2\n2'
    "dict_intern.py", # assert 'true\ntrue\ntrue\ntrue' == 'True\nTrue\nTrue\nTrue'
    "dict_iterator.py", # assert '[[1, 2], [3, 4]]' == '[(1, 2), (3, 4)]'
    "dict_setdefault.py", # assert 'null\nnull\n...n\n42\n1\n\n1' == 'None\nNone\n...2\n1\nNone\n1'
    "equal_class.py", # assert 'false\nfalse...nfalse\nfalse' == 'False\nFalse...nFalse\nFalse'
    "floordivide_intbig.py", # assert '5.1981806420...-1e+41\n1e+41' == '519818064204...0000000000000'
    "for2.py", # assert 'init\ninit' == 'init\n9'
    "fun_annotations.py", # 3]}' == '{1: [2, 3]}'
    "fun_defargs2.py", # "flx...:{"b":"two"}}' == '1 333\n1 333\n2 333\n1 two'
    "int_constfolding_intbig.py", # assert '-1073741823\...23\n-1\n1\n-1' == '-1073741823\...8147419103231'
    "int_divmod.py", # assert '-2 -4 0 -2 [... 4 0 2 [0, 2]' == '-2 -4 0 -2 (... 4 0 2 (0, 2)'
    "int_divmod_intbig.py", # assert '5\n5\n-5\n-5' == '7\n-12\n12\n-7'
    "int_intbig.py", # assert '8589934591\n...91\n& 0\n0\n0' == '8589934591\n...4073709551615'
    "is_isnot.py", # assert 'false\ntrue' == 'False\nTrue'
    "is_isnot_literal.py", # assert 'true\nfalse\...\nfalse\ntrue' == 'True\nFalse\...\nFalse\nTrue'
    "logic_constfolding.py", # assert 'false\n1\nf_...\nfalse\ntrue' == 'False\n1\nf_...\nFalse\nTrue'
    "return1.py", # assert '2\n1\n2 1' == 'None\n1\n2 1'
    "slots_bool_len.py", # assert 'true\n__len_...e\n__len__\n0' == '__bool__\nTr...e\n__len__\n0'
    "special_comparisons.py", # assert 'a == a\ntrue...d != d\nfalse' == 'a == a\nA __...called\nFalse'
    "special_comparisons2.py", # assert 'E eq {}\nfal...e\ntrue\ntrue' == 'E eq F\nFals...nF ne a\n-456'
    "special_methods_intbig.py", # assert 'null' == '126765060022...1496703205376'
    "string_cr_conversion.py", # ef"' == "'abc\\ndef'"
    "string_crlf_conversion.py", # ef"' == "'abc\\ndef'"
    "string_istest.py", # assert 'false\ntrue\...\nfalse\ntrue' == 'False\nTrue\...\nFalse\nTrue'
    "string_repr.py", # u000...0x127: "\x7f"' == "0x00: '\\x00...0x7f: '\\x7f'"
    "string_rfind.py", # assert '2\n2\n2\n-1\...1\n-1\n-1\n-1' == '2\n2\n2\n2\n...1\n-1\n-1\n-1'
    "with_break.py", # assert '0\n1\n2\n3' == '0\n__enter__...t__ None None'
    "with_continue.py", # assert '0\n1\n2\n3\n4' == '0\n__enter__...t__ None None'
    "with_return.py", # assert '4\n[1, 3, 5,...n[1, 3, 5, 7]' == '__enter__ 1\...n(1, 3, 5, 7)'
}

def get_source_files():
    for src in sorted(PROGRAMS_DIR.glob("*.py")):
        if src.name.startswith("set_"):
            continue
        if src.name in DENY_LIST:
            continue
        yield str(src.name)


# @pytest.mark.skip(reason="Too many failures")
@pytest.mark.parametrize("source_file", get_source_files())
def test_module(source_file):
    src = PROGRAMS_DIR / source_file
    py_code = src.read_text()
    if "try:" in py_code:
        # TODO later
        return

    js_code = py2js(src.read_text())

    dst = (Path(tempfile.gettempdir()) / src.name).with_suffix(".js")
    dst.write_text(js_code)

    try:
        p1 = subprocess.run(["node", str(dst)], stdout=subprocess.PIPE, check=True)
        p2 = subprocess.run(["python", str(src)], stdout=subprocess.PIPE, check=True)

        stdout1 = p1.stdout.decode("utf-8").strip()
        stdout2 = p2.stdout.decode("utf-8").strip()

        if stdout1 != stdout2:
            print()
            print()
            print("node result:", stdout1)
            print("python result", stdout2)
            print()
            print(py2js(src.read_text(), include_stdlib=False))

        assert stdout1 == stdout2
    finally:
        os.unlink(dst)
