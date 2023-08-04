from __future__ import annotations

from attr import define, field, mutable

# if typing.TYPE_CHECKING:
#     from .ast import AST


@define
class Scope:
    vars: dict[str, Variable] = field(factory=dict)
    parent: Scope | None = None

    def search(self, name: str) -> Variable | None:
        if name in self.vars:
            return self.vars[name]
        elif self.parent is not None:
            return self.parent.search(name)
        else:
            return None


@mutable
class Variable:
    name: str
    type: str


# @define
# class Symbol:
#     name: str
#
#     # The node where the symbol was defined
#     definition: "AST | None" = None
#
#     def __str__(self):
#         if self.definition is not None:
#             return f"{self.name}: defined by {self.definition}"
#         else:
#             return f"{self.name}"
#
#     def __eq__(self, other):
#         if other is None or type(other) != type(self):
#             return False
#
#         return self.name == other.name
#
#     def __hash__(self):
#         return hash(self.name)
