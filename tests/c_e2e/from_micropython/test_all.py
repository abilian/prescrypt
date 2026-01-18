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
    "andor.py",
    "assign_expr.py",
    "assign_expr_scope.py",
    "builtin_abs_intbig.py",
    "builtin_allany.py",
    "builtin_bin.py",
    "builtin_bin_intbig.py",
    "builtin_callable.py",
    "builtin_dir.py",
    "builtin_ellipsis.py",  # Needs type() and hash() functions
    "builtin_getattr.py",
    "builtin_hash_gen.py",
    "builtin_hash_intbig.py",
    "builtin_hex.py",
    "builtin_hex_intbig.py",
    "builtin_id.py",
    "builtin_len1.py",
    "builtin_locals.py",
    "builtin_map.py",
    "builtin_oct.py",
    "builtin_oct_intbig.py",
    "builtin_print.py",
    "builtin_slice.py",
    "builtin_str_hex.py",
    "builtin_sum.py",
    "class1.py",
    "class3.py",
    "class_bases.py",
    "class_bind_self.py",
    "class_binop.py",
    "class_contains.py",
    "class_dict.py",
    "class_getattr.py",
    "class_inherit1.py",
    "class_inherit_mul.py",
    "class_inplace_op.py",
    "class_number.py",
    "class_reverse_op.py",
    "class_staticclassmethod.py",
    "class_store.py",
    "class_str.py",
    "class_super_aslocal.py",
    "class_super_multinherit.py",
    "class_use_other.py",
    "closure1.py",
    "closure2.py",
    "closure_defargs.py",
    "closure_namedarg.py",
    "compare_multi.py",
    "comprehension1.py",
    "decorator.py",
    "del_subscr.py",
    "dict2.py",
    "dict_clear.py",
    "dict_construct.py",
    "dict_del.py",
    "dict_fromkeys.py",
    "dict_get.py",
    "dict_intern.py",
    "dict_iterator.py",
    "dict_setdefault.py",
    "dict_specialmeth.py",
    "dict_update.py",
    "equal.py",
    "equal_class.py",
    "exception1.py",
    "floordivide_intbig.py",
    "for2.py",
    "fun_annotations.py",
    "fun_calldblstar3.py",
    "fun_callstar.py",
    "fun_defargs2.py",
    "fun_kwonlydef.py",
    "fun_kwvarargs.py",
    "fun_str.py",
    "fun_varargs.py",
    "gen_yield_from.py",
    "gen_yield_from_iter.py",
    "generator1.py",
    "generator2.py",
    "generator_args.py",
    "generator_closure.py",
    "globals_del.py",
    "ifcond.py",
    "int_constfolding_intbig.py",
    "int_divmod.py",
    "int_divmod_intbig.py",
    "int_intbig.py",
    "is_isnot.py",
    "is_isnot_literal.py",
    "iter2.py",
    "iter_of_iter.py",
    "lambda_defargs.py",
    "list_copy.py",
    "list_extend.py",
    "list_slice_3arg.py",
    "list_sort.py",
    "logic_constfolding.py",
    "module1.py",
    "module_dict.py",
    "object1.py",
    "object_dict.py",
    "return1.py",
    "scope.py",
    "scope_class.py",
    "slots_bool_len.py",
    "special_comparisons.py",
    "special_comparisons2.py",
    "special_methods_intbig.py",
    "string_compare.py",
    "string_cr_conversion.py",
    "string_crlf_conversion.py",
    "string_format.py",
    "string_format_cp310.py",
    "string_fstring_debug.py",
    "string_istest.py",
    "string_mult.py",
    "string_repr.py",
    "string_rfind.py",
    "string_slice.py",
    "subclass_native2_list.py",
    "subclass_native2_tuple.py",
    "subclass_native4.py",
    "subclass_native5.py",
    "subclass_native_buffer.py",
    "subclass_native_cmp.py",
    "subclass_native_containment.py",
    "subclass_native_init.py",
    "subclass_native_iter.py",
    "subclass_native_specmeth.py",
    "subclass_native_str.py",
    "sys_path.py",
    "tuple_slice.py",
    "types2.py",
    "unary_op.py",
    "with_break.py",
    "with_continue.py",
    "with_return.py",
}


def get_source_files():
    for src in sorted(PROGRAMS_DIR.glob("*.py")):
        if src.name.startswith("set_"):
            continue
        if src.name in DENY_LIST:
            continue
        yield str(src.name)


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
