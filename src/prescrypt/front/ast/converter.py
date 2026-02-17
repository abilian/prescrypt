from __future__ import annotations

import ast

from . import ast as my_ast


def convert(node: ast.AST) -> my_ast.AST:
    """Converts a "native Python" AST tree to a Prescrypt AST node."""

    class_name = node.__class__.__name__
    cls = getattr(my_ast, class_name)

    fields = cls._fields
    # Arguments for the new node constructor
    # Only include lineno/col_offset for nodes that have _attributes including them
    # (Python 3.14+ deprecates passing these to nodes that don't support them)
    kwargs = {}
    node_attrs = getattr(cls, "_attributes", ())
    if "lineno" in node_attrs:
        kwargs["lineno"] = getattr(node, "lineno", 0)
    if "col_offset" in node_attrs:
        kwargs["col_offset"] = getattr(node, "col_offset", 0)
    children = []
    for k in fields:
        v = getattr(node, k)
        match v:
            case list():
                # Handle lists - could be AST nodes, primitives, or mixed (e.g., kw_defaults has None for missing defaults)
                converted_list = []
                for x in v:
                    if isinstance(x, ast.AST):
                        converted = convert(x)
                        converted_list.append(converted)
                        children.append(converted)
                    else:
                        # Primitive value (string, int, None, etc.) - keep as-is
                        converted_list.append(x)
                kwargs[k] = converted_list
            case ast.AST():
                kwargs[k] = convert(v)
                children.append(kwargs[k])
            case int() | float() | str() | bool() | bytes() | None:
                kwargs[k] = v
            case _ if v is ...:
                # Ellipsis literal
                kwargs[k] = v
            case _:  # pragma: no cover
                msg = f"Unknown type: {type(v)}"
                raise ValueError(msg)

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
