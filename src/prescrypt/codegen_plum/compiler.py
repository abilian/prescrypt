from . import gen_expr


class FakeCompiler:
    def gen_expr(self, expr):
        return gen_expr(expr)


compiler = FakeCompiler()
