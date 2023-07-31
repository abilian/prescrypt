from functools import singledispatch

from prescrypt.ast import ast
from prescrypt.codegen import gen_expr


@singledispatch
def gen_stmt(node: ast.stmt) -> str:
    raise NotImplementedError(f"gen_stmt not implemented for {node!r}")


# def gen_stmt(node_or_nodes: ast.stmt | list[ast.stmt]) -> str:
#     match node_or_nodes:
#         case [*stmts]:
#             return flatten([gen_stmt(node) for node in stmts])
#         case ast.stmt():
#             return flatten(_gen_stmt(node_or_nodes))
#         case _:
#             raise JSError(f"Unexpected node type: {type(node_or_nodes)}")


@gen_stmt.register
def gen_pass(node: ast.Pass):
    return "/* pass */" + "\n"


@gen_stmt.register
def gen_return(node: ast.Return):
    js_value = gen_expr(node.value)
    return f"return {js_value};\n"


# def _gen_stmt(node: ast.stmt) -> str | list:
#     match node:
#         case ast.Pass():
#             return [self.lf("/* pass */")]
#         case ast.Return(value_node):
#             return [self.lf("return " + unify(self.gen_expr(value_node)) + ";")]
#
#         # Exceptions
#         case ast.Raise(exc, cause):
#             return self.gen_raise(exc, cause)
#         case ast.Assert(test_node, msg_node):
#             return self.gen_assert(test_node, msg_node)
#         case ast.Try(body, handlers, orelse, finalbody):
#             return self.gen_try(body, handlers, orelse, finalbody)
#         case ast.TryStar(body, handlers, orelse, finalbody):
#             raise NotImplementedError("TryStar is not supported.")
#         case ast.ExceptHandler(type, name, body):
#             raise NotImplementedError("ExceptHandler is not supported.")
#
#         # Control flow
#         case ast.If(test, body, orelse):
#             return self.gen_if(test, body, orelse)
#         case ast.For(target, iter, body, orelse, type_comment):
#             return self.gen_for(target, iter, body, orelse, type_comment)
#         case ast.AsyncFor(target, iter_node, body, orelse, type_comment):
#             raise NotImplementedError("AsyncFor is not supported.")
#         case ast.While(test, body, orelse):
#             return self.gen_while(test, body, orelse)
#         case ast.Break():
#             # Note that in parse_For, we detect breaks and modify them to
#             # deal with the for-else clause
#             return [self.lf("break;")]
#         case ast.Continue():
#             return [self.lf("continue;")]
#         case ast.Match(subject_node, cases):
#             return self.gen_match(subject_node, cases)
#
#         case ast.With(items, body, type_comment):
#             return self.gen_with(items, body, type_comment)
#         case ast.AsyncWith(items, body, type_comment):
#             raise NotImplementedError("AsyncWith is not supported.")
#         case ast.FunctionDef(name, args, body, decorator_list, returns, type_comment):
#             return self.gen_function_def(
#                 name, args, body, decorator_list, returns, type_comment
#             )
#         case ast.AsyncFunctionDef(
#             name, args, body, decorator_list, returns, type_comment
#         ):
#             raise NotImplementedError("AsyncFunctionDef is not supported.")
#         case ast.ClassDef(name, bases, keywords, body, decorator_list):
#             return self.gen_class_def(name, bases, keywords, body, decorator_list)
#
#         # Variables
#         case ast.Delete(targets):
#             return self.gen_delete(targets)
#         case ast.Assign(targets, value_node, type_comment):
#             return self.gen_assign(targets, value_node, type_comment)
#         case ast.AugAssign(target, op, value_node):
#             return self.gen_aug_assign(target, op, value_node)
#         case ast.AnnAssign(target, annotation, value_node, simple):
#             return self.gen_ann_assign(target, annotation, value_node, simple)
#
#         case ast.Expr(value_node):
#             return self.gen_expr(value_node)
#         case ast.Import(names):
#             return self.gen_import(names)
#         case ast.ImportFrom(module, names, level):
#             return self.gen_import_from(module, names, level)
#         case ast.Global(names):
#             return self.gen_global(names)
#         case ast.Nonlocal(names):
#             return self.gen_nonlocal(names)
#         case _:
#             raise NotImplementedError(f"Statement {node} is not supported.")
