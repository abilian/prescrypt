from __future__ import annotations

from typing import Literal

from attr import define, field, mutable

# Declaration kinds for JavaScript output:
# - "const": single assignment, use `const` in JS
# - "let": multiple assignments, use `let` in JS
# - "none": no declaration needed (globals, nonlocals, parameters in function scope)
DeclarationKind = Literal["const", "let", "none"]


@define
class Scope:
    """Represents a lexical scope in the program.

    Attributes:
        type: The kind of scope ("global", "function", "class", "comprehension")
        vars: Dictionary mapping variable names to Variable objects
        parent: Reference to the enclosing scope, or None for global scope
    """

    type: str = "global"
    vars: dict[str, Variable] = field(factory=dict)
    parent: Scope | None = None

    def search(self, name: str) -> Variable | None:
        """Search for a variable in this scope or any enclosing scope."""
        if name in self.vars:
            return self.vars[name]
        elif self.parent is not None:
            return self.parent.search(name)
        else:
            return None

    def is_global(self) -> bool:
        """Returns True if this is the global (module) scope."""
        return self.parent is None


@mutable
class Variable:
    """Represents a variable binding in a scope.

    Attributes:
        name: The variable name
        type: The kind of binding ("variable", "function", "class", "module",
              "global", "nonlocal")
        is_const: True if the variable is only assigned once (can use `const`)
    """

    name: str
    type: str
    is_const: bool = True

    @property
    def declaration_kind(self) -> DeclarationKind:
        """Determine the JavaScript declaration keyword for this variable.

        Returns:
            "const" for single-assignment local variables
            "let" for reassigned local variables
            "none" for globals, nonlocals, and parameters
        """
        # Globals and nonlocals don't need declaration in their referencing scope
        if self.type in ("global", "nonlocal"):
            return "none"

        # Functions and classes are typically const (defined once)
        if self.type in ("function", "class"):
            return "const"

        # Regular variables: const if single assignment, let otherwise
        return "const" if self.is_const else "let"
