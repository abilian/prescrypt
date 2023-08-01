"""Code generation for statements

Must support:

+ Pass
+ Expr(expr value)

- Global(identifier* names)
- Nonlocal(identifier* names)

- If(expr test, stmt* body, stmt* orelse)
- While(expr test, stmt* body, stmt* orelse)
- For(expr target, expr iter, stmt* body, stmt* orelse, string? type_comment)
- AsyncFor(expr target, expr iter, stmt* body, stmt* orelse, string? type_comment)
- Break
- Continue

- FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list,
    expr? returns, string? type_comment)
- AsyncFunctionDef(identifier name, arguments args, stmt* body,
    expr* decorator_list, expr? returns, string? type_comment)
- ClassDef(identifier name, expr* bases, keyword* keywords, stmt* body,
    expr* decorator_list)
- Return(expr? value)

- Assign(expr* targets, expr value, string? type_comment)
- AugAssign(expr target, operator op, expr value)
- AnnAssign(expr target, expr annotation, expr? value, int simple)
- Delete(expr* targets)

- Raise(expr? exc, expr? cause)
- Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)
- TryStar(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)
- Assert(expr test, expr? msg)

- Import(alias* names)
- ImportFrom(identifier? module, alias* names, int? level)
- With(withitem* items, stmt* body, string? type_comment)
- AsyncWith(withitem* items, stmt* body, string? type_comment)
- Match(expr subject, match_case* cases)

"""

from . import (assignments, classes, control_flow, exceptions, functions,
               simple_statements)

# from . import module
