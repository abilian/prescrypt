import ast

from . import ast as my_ast


def convert(node: ast.mod | ast.AST) -> my_ast.AST:
    class_name = node.__class__.__name__
    cls = getattr(my_ast, class_name)

    fields = cls._fields
    kwargs = {}
    for k in fields:
        v = getattr(node, k)
        match v:
            case [*l]:
                assert all(isinstance(y, ast.AST) for y in v)
                kwargs[k] = [convert(x) for x in v]
            case ast.AST():
                kwargs[k] = convert(v)
            case int() | float() | str() | bool() | None:
                kwargs[k] = v
            case _:
                raise ValueError(f"Unknown type: {type(v)}")

    return cls(**kwargs)


def parse(source: str):
    return convert(ast.parse(source))
