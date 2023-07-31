
# from ._expressions.expr import gen_expr
# from ._statements.stmt import gen_stmt
#
# # Order counts, these asserts are used to prevent reordering and thus circular imports.
# assert gen_expr
# assert gen_stmt
#
# from ._expressions import calls  # noqa
# from ._expressions import constants  # noqa
# from ._expressions import constructors  # noqa
# from ._expressions import misc  # noqa
# from ._expressions import ops  # noqa
# from ._expressions import others  # noqa
#
# from ._statements import module  # noqa
# from ._statements import exceptions  # noqa

from ._statements.module import gen_module

# __all__ = ["gen_expr", "gen_stmt"]

__all__ = ["gen_module"]
