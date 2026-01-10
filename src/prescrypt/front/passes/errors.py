from __future__ import annotations


class BindError(Exception):
    pass


class TypeCheckError(Exception):
    pass


class UnknownSymbolError(BindError):
    def __init__(self, sym, message=None):
        self.sym = sym
        if message is None:
            self.message = f"Unknown symbol: {self.sym}"
        else:
            self.message = message


class StatementOutOfLoopError(BindError):
    def __init__(self, stmt="", message=None):
        if message is None:
            self.message = f"Statement {stmt} is out of a loop"
        else:
            self.message = message


class UnknownTypeError(TypeCheckError):
    def __init__(self, typ, message=None):
        self.typ = typ
        if message is None:
            self.message = f"Unknown type: {self.typ}"
        else:
            self.message = message


class IncompatibleTypeError(TypeCheckError):
    def __init__(self, t1, t2, message=None):
        self.t1 = t1
        self.t2 = t2
        if message is None:
            self.message = f"Operation between incompatile types: {t1} and {t2}"
        else:
            self.message = message
