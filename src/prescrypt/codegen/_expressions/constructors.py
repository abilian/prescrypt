from __future__ import annotations

from prescrypt.codegen.main import CodeGen, gen_expr
from prescrypt.codegen.utils import flatten, unify
from prescrypt.exceptions import JSError
from prescrypt.front import ast


@gen_expr.register
def gen_list(node: ast.List, codegen: CodeGen):
    """Generate list literal with _is_list marker for proper repr().

    Lists display as [1, 2, 3] while tuples display as (1, 2, 3).
    """
    elements = [flatten(codegen.gen_expr(el)) for el in node.elts]
    array_code = "[" + ", ".join(elements) + "]"
    # Mark as list so repr() uses [] instead of ()
    return f"Object.assign({array_code}, {{_is_list: true}})"


@gen_expr.register
def gen_tuple(node: ast.Tuple, codegen: CodeGen):
    elements = [flatten(codegen.gen_expr(el)) for el in node.elts]
    return "[" + ", ".join(elements) + "]"


@gen_expr.register
def gen_set(node: ast.Set, codegen: CodeGen):
    """Generate Set literal: {1, 2, 3} -> new Set([1, 2, 3])"""
    elements = [flatten(codegen.gen_expr(el)) for el in node.elts]
    return f"new Set([{', '.join(elements)}])"


@gen_expr.register
def gen_dict(node: ast.Dict, codegen: CodeGen):
    # Check for dict unpacking (**d) - indicated by None keys
    has_unpacking = any(key is None for key in node.keys)
    if has_unpacking:
        return _gen_dict_with_unpacking(codegen, node.keys, node.values)
    return _gen_dict_fallback(codegen, node.keys, node.values)


def _gen_dict_with_unpacking(
    codegen: CodeGen, keys: list[ast.expr | None], values: list[ast.expr]
) -> str:
    """Generate dict with **unpacking: {**d1, 'a': 1, **d2} -> Object.assign({}, d1, {'a': 1}, d2)"""
    fragments = []
    current_pairs = []  # Collect key-value pairs between unpacking

    for key, val in zip(keys, values):
        if key is None:
            # **dict unpacking - flush current pairs and add the dict to merge
            if current_pairs:
                pair_args = []
                for k, v in current_pairs:
                    pair_args.extend(
                        [unify(gen_expr(k, codegen)), unify(gen_expr(v, codegen))]
                    )
                fragments.append(codegen.call_std_function("create_dict", pair_args))
                current_pairs = []
            # Add the dict being unpacked directly
            fragments.append(unify(gen_expr(val, codegen)))
        else:
            # Regular key-value pair
            current_pairs.append((key, val))

    # Flush remaining pairs
    if current_pairs:
        pair_args = []
        for k, v in current_pairs:
            pair_args.extend([unify(gen_expr(k, codegen)), unify(gen_expr(v, codegen))])
        fragments.append(codegen.call_std_function("create_dict", pair_args))

    if len(fragments) == 1:
        # Single fragment, just use Object.assign to make a copy
        return f"Object.assign({{}}, {fragments[0]})"
    else:
        # Multiple fragments, merge them all
        return f"Object.assign({{}}, {', '.join(fragments)})"


def _gen_dict_fallback(
    codegen: CodeGen, keys: list[ast.expr], values: list[ast.expr]
) -> str:
    func_args = []
    for key, val in zip(keys, values):
        func_args += [
            unify(gen_expr(key, codegen)),
            unify(gen_expr(val, codegen)),
        ]
    # Use call_std_function for usage tracking
    return codegen.call_std_function("create_dict", func_args)
