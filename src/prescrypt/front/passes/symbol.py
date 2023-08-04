from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Symbol:
    name: str

    # The node where the symbol was defined
    definition: Any = None

    def __str__(self):
        if self.definition is not None:
            return f"{self.name}: defined by {self.definition}"
        else:
            return f"{self.name}"

    def __eq__(self, other):
        if other is None or type(other) != type(self):
            return False

        return self.name == other.name

    def __hash__(self):
        return hash(self.name)
