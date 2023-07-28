"""
Draw inheritance hierarchies via Dot (http://www.graphviz.org/)
Author: M. Simionato
E-mail: mis6@pitt.edu
Date: August 2003
License: Python-like
Requires: Python 2.3, dot, standard Unix tools
"""

import ast
import itertools
import os
from pathlib import Path

PSVIEWER = "gv"  # you may change these with
PNGVIEWER = "kview"  # your preferred viewers
PSFONT = "Times"  # you may change these too
PNGFONT = "Courier"  # on my system PNGFONT=Times does not work


def if_(cond, e1, e2=""):
    """Ternary operator would be"""
    if cond:
        return e1
    else:
        return e2


def MRO(cls):
    """Returns the MRO of cls as a text"""
    out = [f"MRO of {cls.__name__}:"]
    for counter, c in enumerate(cls.__mro__):
        name = c.__name__
        bases = ",".join([b.__name__ for b in c.__bases__])
        s = f"  {counter} - {name}({bases})"
        if type(c) is not type:
            s += f"[{type(c).__name__}]"
        out.append(s)

    return "\n".join(out)


class MROgraph:
    def __init__(self, *classes, **options):
        """Generates the MRO graph of a set of given classes."""
        if not classes:
            raise "Missing class argument!"

        filename = options.get("filename", f"MRO_of_{classes[0].__name__}.ps")
        self.labels = options.get("labels", 2)
        caption = options.get("caption", False)
        setup = options.get("setup", "")
        name, dotformat = os.path.splitext(filename)
        format = dotformat[1:]
        fontopt = "fontname=" + if_(format == "ps", PSFONT, PNGFONT)
        nodeopt = f" node [{fontopt}];\n"
        edgeopt = f" edge [{fontopt}];\n"
        viewer = if_(format == "ps", PSVIEWER, PNGVIEWER)
        self.textrepr = "\n".join([MRO(cls) for cls in classes])
        caption = if_(
            caption, f'caption [shape=box,label="{self.textrepr}\n",fontsize=9];'
        ).replace("\n", "\\l")
        setupcode = nodeopt + edgeopt + caption + "\n" + setup + "\n"
        codeiter = itertools.chain(*[self.genMROcode(cls) for cls in classes])
        self.dotcode = "digraph {}{{\n{}{}}}".format(
            name, setupcode, "\n".join(codeiter)
        )

        Path("tmp/ast.dot").write_text(self.dotcode)

        os.system(f"dot -Tpng tmp/ast.dot > {filename}")
        os.system(f"open {filename}")

    def genMROcode(self, cls):
        "Generates the dot code for the MRO of a given class"
        for mroindex, c in enumerate(cls.__mro__):
            name = c.__name__
            manyparents = len(c.__bases__) > 1
            if c.__bases__:
                yield "".join(
                    [
                        " edge [style=solid]; %s -> %s %s;\n"
                        % (
                            b.__name__,
                            name,
                            if_(
                                manyparents and self.labels == 2,
                                '[label="%s"]' % (i + 1),
                            ),
                        )
                        for i, b in enumerate(c.__bases__)
                    ]
                )
            if manyparents:
                yield " {rank=same; %s}\n" % "".join(
                    ['"%s"; ' % b.__name__ for b in c.__bases__]
                )
            number = if_(self.labels, f"{mroindex}-")
            label = f'label="{number + name}"'
            option = if_(
                issubclass(cls, type),  # if cls is a metaclass
                f"[{label}]",
                f"[shape=box,{label}]",
            )
            yield f" {name} {option};\n"
            if type(c) is not type:  # c has a custom metaclass
                metaname = type(c).__name__
                yield f" edge [style=dashed]; {metaname} -> {name};"

    def __repr__(self):
        """ "Returns the Dot representation of the graph"""
        return self.dotcode

    def __str__(self):
        """Returns a text representation of the MRO"""
        return self.textrepr


def get_subclasses(cls):
    for name in dir(ast):
        obj = getattr(ast, name)
        if isinstance(obj, type) and issubclass(obj, cls):
            yield obj


def gen_ast_hierarchy():
    """Generates the MRO graph of the AST hierarchy"""

    classes = get_subclasses(ast.expr)
    MROgraph(*classes, filename="expr.png")

    classes = get_subclasses(ast.stmt)
    MROgraph(*classes, filename="stmt.png")


if __name__ == "__main__":
    gen_ast_hierarchy()
