from prescrypt.ast import ast

from ..main import CodeGen, gen_expr
from ..utils import flatten, unify


@gen_expr.register
def gen_list_comp(node: ast.ListComp, codegen: CodeGen) -> list[str]:
    elt_node, generator_nodes = node.elt, node.generators

    codegen.push_ns("function", "<listcomp>")
    js_elt = flatten(codegen.gen_expr(elt_node))
    js_code = ["(function list_comprehension (iter0) {", "const res = [];"]

    for iter, comprehension in enumerate(generator_nodes):
        assert isinstance(comprehension, ast.comprehension)
        cc = []
        # Get target (can be multiple vars)
        target_node = comprehension.target
        match target_node:
            case ast.Tuple(elts=target_elts):
                target = [flatten(codegen.gen_expr(t)) for t in target_elts]
            case _:
                target = [flatten(codegen.gen_expr(target_node))]

        # comprehension(target_node, iter_node, if_nodes)
        if iter > 0:  # first one is passed to function as an arg
            cc.append(f"let iter# = {flatten(codegen.gen_expr(comprehension.iter))};")

        cc.append(
            'if ((typeof iter# === "object") && '
            "!Array.isArray(iter#)) {iter# = Object.keys(iter#);}"
        )
        cc.append("for (let i#=0; i#<iter#.length; i#++) {")
        cc.append(_iterator_assign("iter#[i#]", *target))

        # Ifs
        if_nodes = comprehension.ifs
        if if_nodes:
            cc.append("if (!(")
            for if_node in if_nodes:
                cc += unify(codegen.gen_expr(if_node))
                cc.append("&&")
            cc.pop(-1)  # pop '&&'
            cc.append(")) {continue;}")

        # Insert code for this comprehension loop
        js_code.append(
            "".join(cc).replace("i#", f"i{iter:d}").replace("iter#", f"iter{iter:d}")
        )

    # Push result
    js_code.append("{res.push(%s);}" % js_elt)

    # End for
    js_code.append("}" * len(generator_nodes))

    # Finalize
    js_code.append("return res;})")  # end function
    iter0 = flatten(codegen.gen_expr(generator_nodes[0].iter))
    js_code.append(f".call(this, {iter0})")  # call funct with iter as 1st arg

    codegen.pop_ns()
    return js_code

    # todo: apply the apply(this) trick everywhere where we use a function


def _iterator_assign(val, *names):
    if len(names) == 1:
        return f"const {names[0]} = {val};"
    else:
        code = []
        for i, name in enumerate(names):
            code.append(f"const {name} = {val}[{i:d}];")
        return " ".join(code)
