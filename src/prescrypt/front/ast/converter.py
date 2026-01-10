from __future__ import annotations

import ast

from . import ast as my_ast


def convert(node: ast.AST) -> my_ast.AST:
    """Converts a "native Python" AST tree to a Prescrypt AST node."""

    class_name = node.__class__.__name__
    cls = getattr(my_ast, class_name)

    fields = cls._fields
    # Arguments for the new node constructor
    kwargs = {
        "lineno": getattr(node, "lineno", 0),
        "col_offset": getattr(node, "col_offset", 0),
    }
    children = []
    for k in fields:
        v = getattr(node, k)
        match v:
            case list():
                # Handle lists - could be AST nodes or primitives (e.g., Global.names is list[str])
                if v and isinstance(v[0], ast.AST):
                    kwargs[k] = [convert(x) for x in v]
                    children += kwargs[k]
                else:
                    # List of primitives (strings, etc.) - keep as-is
                    kwargs[k] = v
            case ast.AST():
                kwargs[k] = convert(v)
                children.append(kwargs[k])
            case int() | float() | str() | bool() | None:
                kwargs[k] = v
            case _:  # pragma: no cover
                raise ValueError(f"Unknown type: {type(v)}")

    new_node = cls(**kwargs)

    # lineno = getattr(node, "lineno", 0)
    # node.lineno = lineno

    new_node._orig_node = node
    for child in children:
        child._parent = new_node

    return new_node


def parse(source: str) -> my_ast.Module:
    tree = convert(ast.parse(source))
    assert isinstance(tree, my_ast.Module)
    return tree
