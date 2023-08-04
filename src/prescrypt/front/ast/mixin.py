from typing import Any

from .scope import Scope


class Mixin:
    _definition: Any = None
    _type: Any = None
    _info: dict | None = None
    _parent: Any = None
    _scope: Scope | None = None

    def __repr__(self):
        return f"<{self.__class__.__name__} (AST node)>"
