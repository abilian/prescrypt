from prescrypt.ast import ast
from prescrypt.exceptions import JSError

from ..main import CodeGen, gen_stmt
from ..utils import flatten, unify


@gen_stmt.register
def gen_assign(node: ast.Assign, codegen: CodeGen):
    """Variable assignment."""

    target_nodes, value_node = node.targets, node.value

    code = [codegen.lf()]

    # Set PScript behavior? Note that its reset on a function exit.
    match target_nodes:
        case [ast.Name(id)]:
            if id == "PSCRIPT_OVERLOAD":
                if self._stack[-1][0] != "function":
                    raise JSError("Can only set PSCRIPT_OVERLOAD inside a function")
                if not isinstance(node.value_node, ast.NameConstant):
                    raise JSError("Can only set PSCRIPT_OVERLOAD with a bool")
                else:
                    self._stack[-1][2]._pscript_overload = bool(node.value_node.value)
                    return []
        case _:
            pass

    # if (
    #     len(target_nodes) == 1
    #     and isinstance(target_nodes[0], ast.Name)
    #     and target_nodes[0].id == "PSCRIPT_OVERLOAD"
    # ):
    #     if self._stack[-1][0] != "function":
    #         raise JSError("Can only set PSCRIPT_OVERLOAD inside a function")
    #     if not isinstance(node.value_node, ast.NameConstant):
    #         raise JSError("Can only set PSCRIPT_OVERLOAD with a bool")
    #     else:
    #         self._stack[-1][2]._pscript_overload = bool(node.value_node.value)
    #         return []

    # Parse targets
    tuple = []
    for target in target_nodes:
        var = flatten(codegen.gen_expr(target))

        match target:
            case ast.Name(id):
                if "." in var:
                    code.append(var)
                else:
                    codegen.add_var(var)
                    code.append(codegen.with_prefix(var))
            case ast.Attribute(value, attr):
                code.append(var)
            case ast.Subscript(value, slice):
                code.append(var)
            case ast.Tuple(elts, ctx):
                dummy = codegen.dummy()
                code.append(dummy)
                tuple = elts
            case ast.List(elts, ctx):
                dummy = codegen.dummy()
                code.append(dummy)
                tuple = elts
            case _:
                raise JSError("Unsupported assignment type")
        code.append(" = ")

    # Parse right side
    if isinstance(value_node, ast.ListComp) and len(node.target_nodes) == 1:
        result_name = codegen.dummy()
        code.append(result_name + ";")
        lc_code = self.parse_ListComp_funtionless(node.value_node, result_name)
        code = [codegen.lf(), result_name + " = [];"] + lc_code + code
    else:
        code += codegen.gen_expr(value_node)
        code.append(";")

    # Handle tuple unpacking
    if tuple:
        code.append(codegen.lf())
        for i, x in enumerate(tuple):
            var = unify(codegen.gen_expr(x))
            if isinstance(x, ast.Name):  # but not when attr or index
                self.vars.add(var)
            code.append("%s = %s[%i];" % (var, dummy, i))

    return code


@gen_stmt.register
def gen_delete(node: ast.Delete, codegen: CodeGen) -> str:
    target_nodes = node.targets
    code = []
    for target in target_nodes:
        code.append(codegen.lf("delete "))
        code += codegen.gen_expr(target)
        code.append(";")
    return flatten(code)
