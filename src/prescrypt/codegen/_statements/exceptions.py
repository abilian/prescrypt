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
            msg = "bare 'raise' outside of except clause"
            raise JSError(msg, node)
        return [codegen.lf(f"throw {exc_var};")]

    if cause_node is not None:
        msg = 'When raising, "cause" is not supported'
        raise JSError(msg, cause_node)
    err_node = exc_node

    # Get cls and msg
    err_cls, err_msg = None, "''"

    match exc_node:
        case ast.Name(id):
            if id.islower():  # raise an (error) object
                return [codegen.lf("throw " + id + ";")]
            err_cls = id
        case ast.Call(func, args, keywords):
            assert isinstance(func, ast.Name)
            err_cls = func.id
            err_msg = "".join([unify(codegen.gen_expr(arg)) for arg in args])
        case _:
            err_msg = "".join(codegen.gen_expr(exc_node))

    err_name = "err_%i" % codegen._indent
    codegen.add_var(err_name)

    # Build code to throw
    if err_cls:
        code = codegen.call_std_function("op_error", [f"'{err_cls}'", err_msg or '""'])
    else:
        code = err_msg

    return [codegen.lf("throw " + code + ";")]


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
    err_type = unify(codegen.gen_expr(type_node)) if type_node else ""
    # Note: err_type is a string like "Exception", not a variable to discard
    if err_type and err_type != "Exception":
        code.append(
            f'if ({err_name} instanceof Error && {err_name}.name === "{err_type}") {{'
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
