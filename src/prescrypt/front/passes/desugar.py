from __future__ import annotations

import ast as _ast
from typing import cast

from prescrypt.front import ast


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

    # -------------------------------------------------------------------------
    # DESIGN ALTERNATIVES (not implemented)
    # -------------------------------------------------------------------------
    # The following visitors represent alternative desugaring strategies that
    # were explored. They lower higher-level constructs to simpler primitives,
    # which can simplify code generation but may lose semantic information.
    #
    # Alternative 1: Lambda as anonymous function assignment
    # -------------------------------------------------------
    # @rewriter
    # def visit_Lambda(self, node: ast.Lambda):
    #     """Desugar lambda to a named function expression.
    #
    #     `lambda x: x + 1` becomes `Function("<lambda>", args, [Return(body)])`
    #
    #     Pros: Uniform handling of all functions
    #     Cons: Loses lambda identity, complicates source maps
    #     """
    #     return Function("<lambda>", node.args, [ast.Return(node.body)])
    #
    # Alternative 2: Function definitions as assignments
    # ---------------------------------------------------
    # @rewriter
    # def visit_FunctionDef(self, node: ast.FunctionDef):
    #     """Desugar `def f(x): body` to `f = Function("f", args, body)`.
    #
    #     Also applies decorators: `@dec def f(): ...` becomes `f = dec(f)`
    #
    #     Pros: Makes function definition explicit as assignment
    #     Cons: Loses hoisting semantics, decorator handling complexity
    #     """
    #     fn = Function(node.name, node.args, node.body)
    #     for d in reversed(node.decorator_list):
    #         fn = ast.Call(d, [fn])
    #     return ast.Assign([ast.Name(node.name, store)], fn)
    #
    # Alternative 3: List comprehensions as explicit loops
    # -----------------------------------------------------
    # @rewriter
    # def visit_ListComp(self, node: ast.ListComp):
    #     """Desugar `[expr for x in iter]` to explicit loop with append.
    #
    #     Becomes:
    #         (lambda .0:
    #             for x in iter:
    #                 for cond in ifs:
    #                     .0.append(expr)
    #             return .0
    #         )([])
    #
    #     Pros: Reduces comprehension to loops (simpler codegen)
    #     Cons: Performance (append vs array literal), loses optimization hints
    #     """
    #     result_append = ast.Attribute(ast.Name(".0", load), "append", load)
    #     body = ast.Expr(ast.Call(result_append, [node.elt]))
    #     for loop in reversed(node.generators):
    #         for test in reversed(loop.ifs):
    #             body = ast.If(test, [body], [])
    #         body = ast.For(loop.target, loop.iter, [body], [])
    #     fn = [body, ast.Return(ast.Name(".0", load))]
    #     args = ast.arguments([ast.arg(".0", None)], None, [], None, [], [])
    #     return ast.Call(Function("<listcomp>", args, fn), [ast.List([], load)])
    # -------------------------------------------------------------------------

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

        return self.visit(ast.BoolOp(ast.And(), groups))

    @rewriter
    def visit_AugAssign(self, node: ast.AugAssign):
        """
        Transforms `a += b` in `a = a + b`.
        """
        import copy as copy_module

        # Create a deep copy of target for use in the expression (with Load context)
        expr_target = copy_module.deepcopy(node.target)
        if isinstance(expr_target, ast.Name):
            expr_target.ctx = ast.Load()

        # Create a deep copy of target for assignment (with Store context)
        assign_target = copy_module.deepcopy(node.target)
        if isinstance(assign_target, ast.Name):
            assign_target.ctx = ast.Store()

        new_node = ast.Assign(
            [assign_target],
            ast.BinOp(expr_target, node.op, node.value),
        )
        new_node.lineno = getattr(node, "lineno", 0)
        return new_node

    @rewriter
    def visit_UnaryOp(self, node: ast.UnaryOp):
        """
        Transforms `-X` to `(0 - X)` and `+X` to `X`.
        """
        match type(node.op):
            case ast.UAdd:
                # Ignore "+" operator
                return node.operand
            case ast.USub:
                return ast.BinOp(ast.Constant(0), ast.Sub(), node.operand)
            case ast.Not | ast.Invert:
                return node
            case _:  # pragma: no cover
                msg = f"UnaryOp {node.op} should not exist"
                raise ValueError(msg)

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
            return node

        left = node.values.pop(0)
        right = self.visit(node)

        return ast.BoolOp(node.op, [left, right])
