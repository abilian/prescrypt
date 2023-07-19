from prescrypt.expr_compiler import ExpressionCompiler


class StatementCompiler(ExpressionCompiler):
    """
    - FunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list, expr? returns, string? type_comment)
    - AsyncFunctionDef(identifier name, arguments args, stmt* body, expr* decorator_list, expr? returns, string? type_comment)
    - ClassDef(identifier name, expr* bases, keyword* keywords, stmt* body, expr* decorator_list)
    - Return(expr? value)
    - Delete(expr* targets)
    - Assign(expr* targets, expr value, string? type_comment)
    - AugAssign(expr target, operator op, expr value)
    - AnnAssign(expr target, expr annotation, expr? value, int simple)
    - For(expr target, expr iter, stmt* body, stmt* orelse, string? type_comment)
    - AsyncFor(expr target, expr iter, stmt* body, stmt* orelse, string? type_comment)
    - While(expr test, stmt* body, stmt* orelse)
    - If(expr test, stmt* body, stmt* orelse)
    - With(withitem* items, stmt* body, string? type_comment)
    - AsyncWith(withitem* items, stmt* body, string? type_comment)
    - Match(expr subject, match_case* cases)
    - Raise(expr? exc, expr? cause)
    - Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)
    - TryStar(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)
    - Assert(expr test, expr? msg)
    - Import(alias* names)
    - ImportFrom(identifier? module, alias* names, int? level)
    - Global(identifier* names)
    - Nonlocal(identifier* names)
    - Expr(expr value)
    - Pass
    - Break
    - Continue
    """
