#
# Exceptions
#
from prescrypt.ast import ast
from prescrypt.exceptions import JSError
from prescrypt.utils import js_repr, unify

from ..main import gen_expr, gen_stmt, CodeGen


@gen_stmt.register
def gen_raise(node: ast.Raise, codegen: CodeGen):
    # We raise the exception as an Error object

    exc_node, cause_node = node.exc, node.cause

    if exc_node is None:
        raise JSError("When raising, provide an error object.")
    if cause_node is not None:
        raise JSError('When raising, "cause" is not supported.')
    err_node = exc_node

    # Get cls and msg
    err_cls, err_msg = None, "''"

    match exc_node:
        case ast.Name(id):
            if id.islower():  # raise an (error) object
                return [codegen.lf("throw " + id + ";")]
            err_cls = id
        case ast.Call(func, args, keywords):
            err_cls = func.name
            err_msg = "".join([unify(gen_expr(arg)) for arg in args])
        case _:
            err_msg = "".join(gen_expr(exc_node))

    err_name = "err_%i" % codegen._indent
    codegen.vars.add(err_name)

    # Build code to throw
    if err_cls:
        code = codegen.call_std_function("op_error", [f"'{err_cls}'", err_msg or '""'])
    else:
        code = err_msg

    return [codegen.lf("throw " + code + ";")]


@gen_stmt.register
def gen_assert(node: ast.Assert, codegen: CodeGen):
    test_node, msg_node = node.test, node.msg

    js_test = gen_expr(test_node)
    js_msg = js_test
    if msg_node:
        js_msg = gen_expr(msg_node)

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
    body, handlers, orelse, finalbody = (
        node.body,
        node.handlers,
        node.orelse,
        node.finalbody,
    )
    if orelse:
        raise JSError("No support for try-else clause.")

    code = []

    # Try
    if True:
        code.append(codegen.lf("try {"))
        codegen._indent += 1
        for n in body:
            code += codegen.gen_stmt(n)
        codegen._indent -= 1
        code.append(codegen.lf("}"))

    # Except
    if handlers:
        codegen._indent += 1
        err_name = "err_%i" % codegen._indent
        code.append(" catch(%s) {" % err_name)
        subcode = []
        for i, handler in enumerate(handlers):
            if i == 0:
                code.append(codegen.lf(""))
            else:
                code.append(" else ")
            subcode = codegen.gen_stmt(handler)
            code += subcode

        # Rethrow?
        if subcode and subcode[0].startswith("if"):
            code.append(" else { throw %s; }" % err_name)

        codegen._indent -= 1
        code.append(codegen.lf("}"))  # end catch

    # Finally
    if finalbody:
        code.append(" finally {")
        codegen._indent += 1
        for n in finalbody:
            code += codegen.gen_stmt(n)
        codegen._indent -= 1
        code.append(codegen.lf("}"))  # end finally

    return code


@gen_stmt.register
def gen_excepthandler(node: ast.ExceptHandler, codegen: CodeGen):
    type, name, body = node.type, node.name, node.body

    err_name = "err_%i" % codegen._indent

    # Set up the catch
    code = []
    err_type = unify(codegen.gen_stmt(type)) if node.type_node else ""
    codegen.vars.discard(err_type)
    if err_type and err_type != "Exception":
        code.append(
            'if (%s instanceof Error && %s.name === "%s") {'
            % (err_name, err_name, err_type)
        )
    else:
        code.append("{")
    codegen._indent += 1
    if node.name:
        code.append(codegen.lf(f"{node.name} = {err_name};"))
        codegen.vars.add(node.name)

    # Insert the body
    for n in node.body_nodes:
        code += gen_stmt(n)
    codegen._indent -= 1

    code.append(codegen.lf("}"))
    return code
