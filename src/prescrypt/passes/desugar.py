import ast as _ast
from typing import cast

from prescrypt.ast import ast


def desugar(tree: ast.Module) -> ast.Module:
    return cast(ast.Module, _desugar(tree))


def _desugar(tree: ast.AST) -> ast.AST:
    return _ast.fix_missing_locations(Desugarer().visit(tree))


def rewriter(rewrite):
    def visit(self, t):
        return _ast.copy_location(rewrite(self, self.generic_visit(t)), t)

    return visit


load, store = ast.Load(), ast.Store()


class Desugarer(ast.NodeTransformer):
    @rewriter
    def visit_Assert(self, node: ast.Assert):
        args = [] if node.msg is None else [node.msg]
        keywords = []
        call = ast.Call(ast.Name("AssertionError", load), args, keywords)
        return ast.If(node.test, [], [ast.Raise(call, None)])

    # @rewriter
    # def visit_Lambda(self, node: ast.Lambda):
    #     return Function("<lambda>", node.args, [ast.Return(node.body)])

    # @rewriter
    # def visit_FunctionDef(self, node: ast.FunctionDef):
    #     fn = Function(node.name, node.args, node.body)
    #     for d in reversed(node.decorator_list):
    #         fn = ast.Call(d, [fn])
    #     return ast.Assign([ast.Name(node.name, store)], fn)

    # @rewriter
    # def visit_ListComp(self, node: ast.ListComp):
    #     result_append = ast.Attribute(ast.Name(".0", load), "append", load)
    #     body = ast.Expr(ast.Call(result_append, [node.elt]))
    #     for loop in reversed(node.generators):
    #         for test in reversed(loop.ifs):
    #             body = ast.If(test, [body], [])
    #         body = ast.For(loop.target, loop.iter, [body], [])
    #     fn = [body, ast.Return(ast.Name(".0", load))]
    #     args = ast.arguments([ast.arg(".0", None)], None, [], None, [], [])
    #     return ast.Call(Function("<listcomp>", args, fn), [ast.List([], load)])

    @rewriter
    def visit_Compare(self, node: ast.Compare):
        """
        Turns `a < b < c` into `a < b and b < c` (from Python doc).
        """
        assert len(node.ops) == len(node.comparators)
        if len(node.ops) == 1:
            return node

        groups = []
        left = node.left
        for i in range(len(node.ops)):
            right = node.comparators[i]
            compare = ast.Compare(left, [node.ops[i]], [right])
            groups.append(compare)
            left = right

        # desugaring the And list as we go
        return self.visit(ast.BoolOp(ast.And(), groups))

    @rewriter
    def visit_AugAssign(self, node: ast.AugAssign):
        """
        Transforms `a += b` in `a = a + b`.
        """
        copy = node.target
        if isinstance(copy, ast.Name):
            copy.ctx = ast.Load()

        new_node = ast.Assign(
            [node.target],
            ast.BinOp(copy, node.op, node.value),
        )
        new_node.lineno = getattr(node, "lineno", 0)
        return new_node

    @rewriter
    def visit_UnaryOp(self, node):
        """
        Transforms `-X` to `(0 - X)` and `+X` to `X`.
        """
        match type(node.op):
            case ast.UAdd:
                return node.operand
            case ast.USub:
                return ast.BinOp(ast.Constant(0), ast.Sub(), node.operand)

    @rewriter
    def visit_BoolOp(self, node: ast.BoolOp):
        """
        Turns a BoolOp with more than 2 values into multiple BoolOp within each other.

        For some reason, BoolOp is not a binary operator.
        `1 and 2 and 3` is a single node in the ast, but this is a problem for
        later translation. So turning into a chain of binary nodes
        """
        assert len(node.values) > 1
        if len(node.values) == 2:
            # the node is binary, stop here
            return node

        left = node.values.pop(0)
        right = self.visit(node)

        return ast.BoolOp(node.op, [left, right])
