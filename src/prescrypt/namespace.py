from __future__ import annotations

LOCAL = 1
NONLOCAL = 2
GLOBAL = 3
GLOBAL_SUB = 4


class NameSpace(dict):
    """Representation of the namespace in a certain scope. It looks a bit like
    a set, but makes a distinction between used/defined and local/nonlocal.

    The value of an item in this dict can be:
    * 1: variable defined in this scope.
    * 2: nonlocal variable (set nonlocal in this scope).
    * 3: global variable (set global in this scope).
    * 4: global variable (set in a subscope).
    * set: variable used here (or in a subscope) but not defined here.
    """

    def set_nonlocal(self, key):
        """Explicitly declare a name as nonlocal."""
        self[key] = NONLOCAL  # also if already exists

    def set_global(self, key):
        """Explicitly declare a name as global."""
        self[key] = GLOBAL  # also if already exists
        # becomes 4 in parent scope

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

        Undefined variables and nonlocals are moved upwards.
        """
        for name in sub.get_globals():
            sub.discard(name)
            if name not in self:
                self[name] = GLOBAL_SUB
            # elif self[name] not in (3, 4):  ... dont know whether outer scope
            #     raise JSError('Cannot use non-global that is global in subscope.')
        for name, hows in sub.get_undefined():
            sub.discard(name)
            for how in hows:
                self.use(name, how)

    def is_known(self, name):
        """Get whether the given name is defined or declared global/nonlocal in
        this scope."""
        return self.get(name, 0) in (LOCAL, NONLOCAL, GLOBAL)

    def get_defined(self):
        """Get list of variable names that the current scope defines."""
        return {name for name, val in self.items() if val == LOCAL}

    def get_globals(self):
        """Get list of variable names that are declared global in the current
        scope or its subscopes."""
        return {name for name, val in self.items() if val in (GLOBAL, GLOBAL_SUB)}

    def get_undefined(self):
        """Get (name, set) tuples for variables that are used, but not defined.

        The set contains the ways in which the variable is used (e.g.
        name.foo.bar).
        """
        return [(name, val) for name, val in self.items() if isinstance(val, set)]


# class Stack:
#     def __init__(self):
#         self.stack = []
#
#     def push(self, item):
#         self.stack.append(item)
#
#     def pop(self):
#         return self.stack.pop()
#
#     def push(self, type, name):
#         """New namespace stack.
#
#         Match a call to this with a call to pop_stack() and process the
#         resulting line to declare the used variables. type must be
#         'module', 'class' or 'function'.
#         """
#         assert type in ("module", "class", "function")
#         self._stack.append((type, name, NameSpace()))
#
#     def pop(self):
#         """Pop the current stack and return the namespace."""
#         # Pop
#         nstype, nsname, ns = self._stack.pop(-1)
#         self.vars.leak_stack(ns)
#         return ns
