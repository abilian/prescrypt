from prescrypt.ast import ast
from prescrypt.exceptions import JSError

from ..main import CodeGen, gen_stmt
from ..utils import flatten


@gen_stmt.register
def gen_assign(node: ast.Assign, codegen: CodeGen):
    """Variable assignment."""

    target_nodes, value_node = node.targets, node.value

    js_value = flatten(codegen.gen_expr(value_node))

    if len(target_nodes) > 1:
        raise JSError("Multiple assignment not (yet) supported.")

    target_node = target_nodes[0]

    match target_node:
        case ast.Name(id):
            if codegen.ns.is_known(id):
                return f"{codegen.with_prefix(id)} = {js_value};"
            else:
                codegen.add_var(id)
                return f"let {codegen.with_prefix(id)} = {js_value};"

        case ast.Attribute(value, attr):
            js_target = flatten(codegen.gen_expr(target_node))
            return f"{js_target} = {js_value};"

        case ast.Subscript(value, slice):
            js_target = flatten(codegen.gen_expr(target_node))
            return f"{js_target} = {js_value};"

        case _:
            raise NotImplementedError(f"gen_assign not implemented for {node!r}")

    #
    # code = [codegen.lf()]
    #
    # # Parse targets
    # tuple = []
    # dummy = ""
    # for target in target_nodes:
    #     var = flatten(codegen.gen_expr(target))
    #
    #     match target:
    #         case ast.Name(id):
    #             if "." in var:
    #                 code.append(var)
    #             else:
    #                 codegen.add_var(var)
    #                 code.append(codegen.with_prefix(var))
    #         case ast.Attribute(value, attr):
    #             code.append(var)
    #         case ast.Subscript(value, slice):
    #             code.append(var)
    #         case ast.Tuple(elts, ctx):
    #             dummy = codegen.dummy()
    #             code.append(dummy)
    #             tuple = elts
    #         case ast.List(elts, ctx):
    #             dummy = codegen.dummy()
    #             code.append(dummy)
    #             tuple = elts
    #         case _:
    #             raise JSError(f"Unsupported assignment type: {target}")
    #
    #     code.append(" = ")
    #
    # # Parse right side
    # if isinstance(value_node, ast.ListComp) and len(node.target_nodes) == 1:
    #     result_name = codegen.dummy()
    #     code.append(result_name + ";")
    #     lc_code = self.parse_ListComp_funtionless(node.value_node, result_name)
    #     code = [codegen.lf(), result_name + " = [];"] + lc_code + code
    # else:
    #     code += codegen.gen_expr(value_node)
    #     code.append(";")
    #
    # # Handle tuple unpacking
    # if tuple:
    #     code.append(codegen.lf())
    #     for i, x in enumerate(tuple):
    #         var = unify(codegen.gen_expr(x))
    #         if isinstance(x, ast.Name):  # but not when attr or index
    #             codegen.add_var(var)
    #         code.append("%s = %s[%i];" % (var, dummy, i))
    #
    # return code


@gen_stmt.register
def gen_delete(node: ast.Delete, codegen: CodeGen) -> str:
    target_nodes = node.targets
    code = []
    for target in target_nodes:
        code.append(codegen.lf("delete "))
        code += codegen.gen_expr(target)
        code.append(";")
    return flatten(code)
