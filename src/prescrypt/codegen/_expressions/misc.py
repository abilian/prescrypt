#
# The rest
#
from buildstr import Builder

from prescrypt.ast import ast
from prescrypt.utils import unify

from ..main import gen_expr, CodeGen


@gen_expr.register
def gen_if_exp(node: ast.IfExp, codegen: CodeGen) -> list[str]:
    # in "a if b else c"
    body, test, orelse = node.body, node.test, node.orelse

    js_body = codegen.gen_expr(body)
    js_test = codegen.gen_truthy(test)
    js_else = codegen.gen_expr(orelse)

    code = Builder()
    with code(surround="()"):
        code << js_test
    code << "?"
    with code(surround="()"):
        code << js_body
    code << ":"
    with code(surround="()"):
        code << js_else
    return code.build()


@gen_expr.register
def gen_list_comp(node: ast.ListComp, codegen: CodeGen) -> list[str]:
    # Note: generators is a list of ast.comprehension
    # ast.comprehension has attrs: 'target', 'iter', 'ifs', 'is_async',
    elt, generators = node.elt, node.generators

    self.push_stack("function", "listcomp")
    elt = "".join(codegen.gen_expr(elt))
    code = ["(function list_comprehension (iter0) {", "var res = [];"]
    vars = []

    for iter, comprehension in enumerate(generators):
        cc = []
        # Get target (can be multiple vars)
        if isinstance(comprehension.target, ast.Tuple):
            target = ["".join(gen_expr(t)) for t in comprehension.target]
        else:
            target = ["".join(gen_expr(comprehension.target))]

        for t in target:
            vars.append(t)
        vars.append("i%i" % iter)

        # comprehension(target_node, iter_node, if_nodes)
        if iter > 0:  # first one is passed to function as an arg
            cc.append(f"iter# = {''.join(gen_expr(comprehension.iter_node))};")
            vars.append("iter%i" % iter)
        cc.append(
            'if ((typeof iter# === "object") && '
            "(!Array.isArray(iter#))) {iter# = Object.keys(iter#);}"
        )
        cc.append("for (i#=0; i#<iter#.length; i#++) {")
        cc.append(self._iterator_assign("iter#[i#]", *target))

        # Ifs
        if comprehension.if_nodes:
            cc.append("if (!(")
            for iff in comprehension.if_nodes:
                cc += unify(gen_expr(iff))
                cc.append("&&")
            cc.pop(-1)  # pop '&&'
            cc.append(")) {continue;}")

        # Insert code for this comprehension loop
        code.append(
            "".join(cc).replace("i#", "i%i" % iter).replace("iter#", "iter%i" % iter)
        )

    # Push result
    code.append("{res.push(%s);}" % elt)
    for comprehension in node.comp_nodes:
        code.append("}")  # end for
    # Finalize
    code.append("return res;})")  # end function
    iter0 = "".join(self.parse(node.comp_nodes[0].iter_node))
    code.append(".call(this, " + iter0 + ")")  # call funct with iter as 1st arg
    code.insert(2, f"var {', '.join(vars)};")
    # Clean vars
    for var in vars:
        self.vars.add(var)
    self.pop_stack()
    return code

    # todo: apply the apply(this) trick everywhere where we use a function
