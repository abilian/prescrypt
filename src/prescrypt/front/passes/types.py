from __future__ import annotations

from .singleton import Singleton


class Int(metaclass=Singleton):
    """
    Int type singleton.
    """

    def compatible_with(self, other):
        return other == self


class Float(metaclass=Singleton):
    """
    Float type singleton.
    """

    def compatible_with(self, other):
        return other == self


class Bool(metaclass=Singleton):
    """
    Bool type singleton.
    """

    def compatible_with(self, other):
        return other == self


class String(metaclass=Singleton):
    """
    String type singleton.
    """

    def compatible_with(self, other):
        return other == self


class Void(metaclass=Singleton):
    """
    Void type singleton.
    """

    def compatible_with(self, other):
        return False


class Unknown(metaclass=Singleton):
    """
    Unknown type singleton - used when type cannot be inferred.
    """

    def compatible_with(self, other):
        return True  # Unknown is compatible with anything


class List(metaclass=Singleton):
    """
    List type singleton.
    """

    def compatible_with(self, other):
        return other == self


class Dict(metaclass=Singleton):
    """
    Dict type singleton.
    """

    def compatible_with(self, other):
        return other == self


class Tuple(metaclass=Singleton):
    """
    Tuple type singleton.
    """

    def compatible_with(self, other):
        return other == self


class JSObject(metaclass=Singleton):
    """
    JavaScript object type singleton.

    Used to mark variables that hold JavaScript objects (from browser APIs,
    callbacks, etc.) so the compiler treats method calls as native JS calls
    rather than Python stdlib calls.

    Usage:
        from typing import TYPE_CHECKING
        if TYPE_CHECKING:
            from prescrypt import JS

        result: JS = some_js_callback()
        value = result.get("key")  # Treated as JS .get(), not _pymeth_get
    """

    def compatible_with(self, other):
        return other == self


# Alias for user code
JS = JSObject
