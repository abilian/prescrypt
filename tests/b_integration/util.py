from __future__ import annotations

import ast
import random
from typing import Callable

from attr import mutable


@mutable
class __Generator:
    """
    Internal class. Do not use.
    """

    max_complexity: int = 10
    complexity: int = 0

    def _randomize(self, cases: list[Callable]):
        return random.choice(cases)()

    def gen_expr(self) -> ast.Expression:
        return ast.Expression(self.gen_atom(), lineno=0, col_offset=0)

    def gen_atom(self) -> ast.AST:
        """
        | NAME
        | 'True'
        | 'False'
        | 'None'
        | strings
        | NUMBER
        | (tuple | group | genexp)
        | (list | listcomp)
        | (dict | set | dictcomp | setcomp)
        | '...'
        """
        return self._randomize(
            [
                # self.gen_name,
                self.gen_true,
                self.gen_false,
                self.gen_none,
                self.gen_string,
                self.gen_number,
                self.gen_tuple,
                self.gen_list,
                self.gen_dict,
                # No sets in JS
                # self.gen_set,
                # No ellipsis in JS
                # self.gen_ellipsis,
                # Not yet implemented
                # self.gen_listcomp,
                # self.gen_group,
                # self.gen_genexp,
                # self.gen_dictcomp,
                # self.gen_setcomp,
            ]
        )

    def gen_name(self):
        return ast.Name(id=random.choice("abcdefg"))

    def gen_true(self):
        return ast.Constant(value=True)

    def gen_false(self):
        return ast.Constant(value=False)

    def gen_none(self):
        return ast.Constant(value=None)

    def gen_string(self):
        return ast.Constant(value=random.choice(["", "a", "abc", "abc def"]))

    def gen_number(self):
        rnd = random.randint(0, 3)
        match rnd:
            case 0:
                return ast.Constant(0)
            case 1:
                return ast.Constant(0.0)
            case 2:
                return ast.Constant(random.randint(-1000, 1000))
            case 3:
                return ast.Constant(random.uniform(-10, 10))

    def gen_tuple(self):
        if self.complexity > self.max_complexity:
            return ast.Tuple([])
        else:
            self.complexity += 1
            return ast.Tuple([self.gen_atom() for _ in range(3)])

    def gen_list(self):
        if self.complexity > self.max_complexity:
            return ast.List([])
        else:
            self.complexity += 1
            return ast.List([self.gen_atom() for _ in range(3)])

    def gen_dict(self):
        # Note: only generate dicts with string keys because JavaScript.
        if self.complexity > self.max_complexity:
            return ast.Dict([], [])
        else:
            self.complexity += 1
            keys = [self.gen_string() for _ in range(3)]
            values = [self.gen_atom() for _ in range(3)]
            # keys = [self.gen_atom() for _ in range(3)]
            return ast.Dict(keys, values)

    def gen_set(self):
        if self.complexity > self.max_complexity:
            return ast.Set([])
        else:
            self.complexity += 1
            return ast.Set(elts=[self.gen_atom() for _ in range(3)])

    def gen_ellipsis(self):
        return ast.Ellipsis()


def gen_expr():
    """Generate a random expression as a string"""
    return ast.unparse(__Generator().gen_expr())
