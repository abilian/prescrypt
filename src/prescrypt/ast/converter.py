import ast

from . import ast as my_ast


def convert(node: ast.mod | ast.AST) -> my_ast.AST:
    """Converts a "native Python" AST tree to a Prescrypt AST node."""

    class_name = node.__class__.__name__
    cls = getattr(my_ast, class_name)

    fields = cls._fields
    kwargs = {}
    for k in fields:
        v = getattr(node, k)
        match v:
            case list():
                assert all(isinstance(y, ast.AST) for y in v)
                kwargs[k] = [convert(x) for x in v]
            case ast.AST():
                kwargs[k] = convert(v)
            case int() | float() | str() | bool() | None:
                kwargs[k] = v
            case _:  # pragma: no cover
                raise ValueError(f"Unknown type: {type(v)}")

    new_node = cls(**kwargs)

    lineno = getattr(node, "lineno", 0)
    node.lineno = lineno

    new_node._orig_node = node

    return new_node


def parse(source: str) -> my_ast.Module:
    tree = convert(ast.parse(source))
    assert isinstance(tree, my_ast.Module)
    return tree
