from __future__ import annotations

from prescrypt.codegen.main import CodeGen, gen_expr
from prescrypt.front import ast

MAP = {True: "true", False: "false", None: "null"}


@gen_expr.register
def gen_constant(node: ast.Constant, codegen: CodeGen):
    match node:
        case ast.Constant(bool(value)):
            return str(value).lower()

        case ast.Constant(int(n)):
            return str(n)

        case ast.Constant(str(s)):
            return repr(s)

        case ast.Constant(float(s)):
            return str(s)

        case ast.Constant(None):
            return "null"

        case ast.Constant(bytes(b)):
            # Convert bytes to Uint8Array: b"hello" -> new Uint8Array([104, 101, 108, 108, 111])
            byte_values = ", ".join(str(byte) for byte in b)
            return f"new Uint8Array([{byte_values}])"

        case ast.Constant(value) if value is ...:
            # Ellipsis literal: ... -> Symbol.for('Ellipsis')
            # Using Symbol.for ensures ... === Ellipsis is true
            return "Symbol.for('Ellipsis')"

        case _:  # pragma: no cover
            msg = f"Unknown Constant: {node}"
            raise ValueError(msg)
