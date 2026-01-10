"""
Namespace tracking for variable scoping during code generation.

DESIGN NOTE: Scope Implementation Alternatives
==============================================

This codebase has multiple scope-tracking implementations with different purposes:

1. `front/ast/scope.py` - Scope/Variable (attrs classes)
   - Simple parent-linked scope chain
   - Used by Binder for semantic analysis
   - Tracks variable constness (single vs multiple assignment)

2. `front/passes/scope.py` - Scope (Visitor class)
   - Python closure semantics (cellvars, freevars, derefvars)
   - Based on Tailbiter/Compylo
   - For analyzing variable capture in closures

3. `front/passes/scopes.py` - ScopedMap
   - Symbol-based scope tracking
   - Stack of named scopes with Symbol objects

4. This file (`namespace.py`) - NameSpace (dict subclass)
   - Used during code generation (not semantic analysis)
   - Tracks how variables are accessed (local/nonlocal/global)
   - Supports scope leaking for nested function variable hoisting
   - Originally from PScript for JavaScript var declaration generation

The key difference: Binder's Scope tracks what variables exist and their properties,
while NameSpace tracks how to declare them in the generated JavaScript output
(var, let, const, or nothing for globals).

TODO: Consider consolidating these implementations or clearly documenting
when each should be used.
"""
from __future__ import annotations

LOCAL = 1
NONLOCAL = 2
GLOBAL = 3
GLOBAL_SUB = 4


class NameSpace(dict):
    """Representation of the namespace in a certain scope for code generation.

    Tracks variables and their declaration requirements for JavaScript output.
    It looks a bit like a set, but makes a distinction between used/defined
    and local/nonlocal.

    The value of an item in this dict can be:
    * 1 (LOCAL): variable defined in this scope (needs `var`/`let` declaration)
    * 2 (NONLOCAL): nonlocal variable (set nonlocal in this scope)
    * 3 (GLOBAL): global variable (set global in this scope)
    * 4 (GLOBAL_SUB): global variable (set in a subscope)
    * set: variable used here (or in a subscope) but not defined here
    """

    def set_nonlocal(self, key):
        """Explicitly declare a name as nonlocal."""
        self[key] = NONLOCAL  # also if already exists

    def set_global(self, key):
        """Explicitly declare a name as global."""
        self[key] = GLOBAL  # also if already exists

    def use(self, key, how):
        """Declare a name as used and how (the full name.foo.bar).

        The name may be defined in higher level, or it will end up in
        vars_unknown.
        """
        hows = self.setdefault(key, set())
        if isinstance(hows, set):
            hows.add(how)

    def add(self, key):
        """Declare a name as defined in this namespace."""
        # If value is 4, the name is used as a global in a subscope. At this
        # point, we do not know whether this is the toplevel scope (also
        # because py2js() is often used to transpile snippets which are later
        # combined), so we assume that the user know what (s)he is doing.
        curval = self.get(key, 0)
        # don't overwrite nonlocal or global
        if curval not in (NONLOCAL, GLOBAL):
            self[key] = 1

    def discard(self, key):
        """Discard name from this namespace."""
        self.pop(key, None)

    def leak_stack(self, sub):
        """Leak a child namespace into the current one.

        When a nested function/class scope is popped, undefined variables and
        nonlocals need to be propagated upward. This is essential for:

        1. JavaScript `var` hoisting - variables used in inner scopes but
           defined in outer scopes need to be declared in the outer scope

        2. Closure variable tracking - knowing which variables are captured

        Example:
            def outer():
                def inner():
                    return x  # x is undefined in inner, should be found in outer
                x = 1
        """
        for name in self.get_globals():
            sub.discard(name)
            if name not in self:
                self[name] = GLOBAL_SUB
        for name, hows in sub.get_undefined():
            sub.discard(name)
            for how in hows:
                self.use(name, how)

    def is_known(self, name):
        """Get whether the given name is defined or declared global/nonlocal in
        this scope."""
        return self.get(name, 0) in (LOCAL, NONLOCAL, GLOBAL)

    def get_defined(self):
        """Get list of variable names that the current scope defines.

        These are the names that need `var`/`let` declarations in JavaScript.
        """
        return {name for name, val in self.items() if val == LOCAL}

    def get_globals(self):
        """Get list of variable names that are declared global in the current
        scope or its subscopes."""
        return {name for name, val in self.items() if val in (GLOBAL, GLOBAL_SUB)}

    def get_undefined(self):
        """Get (name, set) tuples for variables that are used, but not defined.

        The set contains the ways in which the variable is used (e.g.
        name.foo.bar). These may need to be resolved in an enclosing scope.
        """
        return [(name, val) for name, val in self.items() if isinstance(val, set)]
