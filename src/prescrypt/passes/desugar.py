import ast
from ast import NodeTransformer


class DesugarVisitor(NodeTransformer):
    # def __desugar_IntString(self, right, left):
    #     st = right if right.typ == String else left
    #     num = right if right.typ == Int else left
    #     # FIXME: st/num can also be Subscript, Name, Function...
    #     match st, num:
    #         case ast.Constant, ast.Constant:
    #             return ast.Constant(st.value * num.value)
    #         case _:
    #             return None
    #
    # def visit_BinOp(self, node):
    #     """
    #     @brief          Desugaring common BinOp tricks, such as `a * "a"`
    #     @param  node    BinOp to be visited
    #     """
    #     if type(node.op) != ast.Mult:
    #         return node
    #
    #     match (node.left.typ, node.right.typ):
    #         case (String, Int) | (Int, String):
    #             res = self.__desugar_IntString(node.right, node.left)
    #             return res if res is not None else node
    #         case _:
    #             return node

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

    def visit_AugAssign(self, node: ast.AugAssign):
        """
        Transforms `a += b` in `a = a + b`.
        """
        copy = node.target
        if isinstance(copy, ast.Name):
            copy.ctx = ast.Load()

        return ast.Assign([node.target], ast.BinOp(copy, node.op, node.value))

    def visit_UnaryOp(self, node):
        """
        Transforms `-X` to `(0 - X)` and `+X` to `X`.
        """
        match type(node.op):
            case ast.UAdd:
                return node.operand
            case ast.USub:
                return ast.BinOp(ast.Constant(0), ast.Sub(), node.operand)

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


def desugar(tree: ast.AST) -> ast.AST:
    """
    Desugar the tree in place.
    """
    return DesugarVisitor().visit(tree)
