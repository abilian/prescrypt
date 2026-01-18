#
# Exceptions
#
from __future__ import annotations

from prescrypt.codegen.main import CodeGen, gen_stmt
from prescrypt.codegen.utils import js_repr, unify
from prescrypt.exceptions import JSError
from prescrypt.front import ast


@gen_stmt.register
def gen_raise(node: ast.Raise, codegen: CodeGen):
    # We raise the exception as an Error object

    exc_node, cause_node = node.exc, node.cause

    # Bare raise - re-raise current exception
    if exc_node is None:
        exc_var = codegen._get_exception_var()
        if exc_var is None:
            # Outside except block: raise RuntimeError at runtime
            # (Python raises "RuntimeError: No active exception to re-raise")
            err_code = codegen.call_std_function(
                "op_error", ["'RuntimeError'", "'No active exception to re-raise'"]
            )
            return [codegen.lf(f"throw {err_code};")]
        return [codegen.lf(f"throw {exc_var};")]

    # Get cls and msg
    err_cls, err_msg = None, "''"

    match exc_node:
        case ast.Name(id):
            if id.islower():  # raise an (error) object
                if cause_node is not None:
                    # raise obj from cause -> obj.__cause__ = cause; throw obj
                    js_cause = unify(codegen.gen_expr(cause_node))
                    return [
                        codegen.lf(f"{id}.__cause__ = {js_cause};"),
                        codegen.lf(f"throw {id};"),
                    ]
                return [codegen.lf("throw " + id + ";")]
            err_cls = id
        case ast.Call(func, args, keywords):
            assert isinstance(func, ast.Name)
            err_cls = func.id
            err_msg = ", ".join([unify(codegen.gen_expr(arg)) for arg in args])
        case _:
            err_msg = "".join(codegen.gen_expr(exc_node))

    err_name = "err_%i" % codegen._indent
    codegen.add_var(err_name)

    # Build code to throw
    if err_cls:
        exc_code = codegen.call_std_function(
            "op_error", [f"'{err_cls}'", err_msg or '""']
        )
    else:
        exc_code = err_msg

    # Handle exception chaining: raise X from Y
    if cause_node is not None:
        js_cause = unify(codegen.gen_expr(cause_node))
        tmp_var = codegen.dummy("exc")
        return [
            codegen.lf(f"let {tmp_var} = {exc_code};"),
            codegen.lf(f"{tmp_var}.__cause__ = {js_cause};"),
            codegen.lf(f"throw {tmp_var};"),
        ]

    return [codegen.lf("throw " + exc_code + ";")]


@gen_stmt.register
def gen_assert(node: ast.Assert, codegen: CodeGen):
    test_node, msg_node = node.test, node.msg

    js_test = codegen.gen_expr(test_node)
    js_msg = js_test
    if msg_node:
        js_msg = codegen.gen_expr(msg_node)

    code = []
    code.append(codegen.lf("if (!("))
    code += js_test
    code.append(")) { throw ")
    code.append(
        codegen.call_std_function("op_error", ["'AssertionError'", js_repr(js_msg)])
    )
    code.append(";}")
    return code


@gen_stmt.register
def gen_try(node: ast.Try, codegen: CodeGen):
    body_nodes = node.body
    handler_nodes = node.handlers
    orelse_nodes = node.orelse
    finalbody_nodes = node.finalbody

    code = []
    has_else = bool(orelse_nodes)

    # If there's an else clause, we need a flag to track if exception occurred
    exc_flag = None
    if has_else:
        exc_flag = f"_no_exc_{codegen._indent}"
        code.append(codegen.lf(f"let {exc_flag} = true;"))

    # Try
    code.append(codegen.lf("try {"))
    codegen.indent()
    for n in body_nodes:
        code += codegen.gen_stmt(n)
    codegen.dedent()
    code.append(codegen.lf("}"))

    # Except
    if handler_nodes:
        codegen.indent()
        err_name = "err_%i" % codegen._indent

        # Track exception variable for bare raise support
        codegen._push_exception_var(err_name)

        code.append(" catch(%s) {" % err_name)

        # If there's an else clause, set the flag to false when entering catch
        if has_else:
            code.append(codegen.lf(f"{exc_flag} = false;"))

        subcode = []
        for i, handler in enumerate(handler_nodes):
            if i == 0:
                code.append(codegen.lf(""))
            else:
                code.append(" else ")
            subcode = codegen.gen_stmt(handler)
            code += subcode

        # Rethrow?
        if subcode and subcode[0].startswith("if"):
            code.append(" else { throw %s; }" % err_name)

        codegen._pop_exception_var()
        codegen.dedent()
        code.append(codegen.lf("}"))  # end catch

    # Else clause - runs if no exception was raised
    if has_else:
        code.append(codegen.lf(f"if ({exc_flag}) {{"))
        codegen.indent()
        for n in orelse_nodes:
            code += codegen.gen_stmt(n)
        codegen.dedent()
        code.append(codegen.lf("}"))

    # Finally
    if finalbody_nodes:
        code.append(" finally {")
        codegen.indent()
        for n in finalbody_nodes:
            code += codegen.gen_stmt(n)
        codegen.dedent()
        code.append(codegen.lf("}"))  # end finally

    return code


@gen_stmt.register
def gen_excepthandler(node: ast.ExceptHandler, codegen: CodeGen):
    type_node, name_node, body_nodes = node.type, node.name, node.body

    err_name = "err_%i" % codegen._indent

    # Set up the catch
    code = []

    # Get the exception type name for the check
    # We need the original Python name (e.g., "ValueError"), not the JS identifier
    if type_node:
        if isinstance(type_node, ast.Name):
            # Simple name like ValueError, TypeError, etc.
            exc_name = type_node.id
        else:
            # For more complex expressions, fall back to generated code
            exc_name = unify(codegen.gen_expr(type_node))
    else:
        exc_name = ""

    # Note: err_type is a string like "Exception", not a variable to discard
    if exc_name and exc_name != "Exception":
        # Check both name property (for op_error exceptions) and instanceof (for class-based exceptions)
        # Also generate the JS identifier for the isinstance check
        js_exc_type = unify(codegen.gen_expr(type_node)) if type_node else ""
        code.append(
            f'if ({err_name} instanceof Error && ({err_name}.name === "{exc_name}" || {err_name} instanceof {js_exc_type})) {{'
        )
    else:
        code.append("{")
    codegen.indent()
    if node.name:
        code.append(codegen.lf(f"{node.name} = {err_name};"))
        codegen.add_var(node.name)

    # Insert the body
    for n in node.body:
        code += codegen.gen_stmt(n)
    codegen.dedent()

    code.append(codegen.lf("}"))
    return code
