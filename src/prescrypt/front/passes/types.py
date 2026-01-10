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
