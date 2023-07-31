from .constructors import *  # noqa
from .functions import *  # noqa
from .internals import *  # noqa
from .methods import *  # noqa


class Stdlib:
    def __init__(self):
        self._std_functions = {}
        self._std_methods = {}

        for name, obj in globals().items():
            if not callable(obj):
                continue

            if name.startswith("function_"):
                self._std_functions[name[9:]] = obj
            elif name.startswith("method_"):
                self._std_methods[name[7:]] = obj
            else:
                pass

    def get_function(self, name, default=None):
        return self._std_functions.get(name, default)

    def get_method(self, name, default=None):
        return self._std_methods.get(name, default)
