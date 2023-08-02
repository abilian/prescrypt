REGRESSIONS = ["[1, 2, 'a', -1]"]

EXPRESSIONS = REGRESSIONS + [
    #
    # Literals
    #
    "1",
    "1.0",
    "1e3",
    "1e-3",
    "True",
    "False",
    "None",
    "'a'",
    '"a"',
    #
    # Arithmetic ops
    #
    "+1",
    "-1",
    "~1",
    "1+1",
    "2 * 3 + 5 * 6",
    "1 // 2",
    "1 % 2",
    "2 ** 2",
    #
    # Float ops
    #
    "-1.0",
    "1.0 + 1.0",
    "1.0 - 1.0",
    "1.0 * 1.0",
    "1.0 / 1.0",
    "1 / 2",
    "1.0 // 2.0",
    "1.0 % 2.0",
    "2.0 ** 2.0",
    #
    # String ops
    #
    "3 * 'a'",
    "'a' + 'b'",
    '"a" + "b"',
    #
    # Boolean ops
    #
    "True or False",
    "True and False",
    "not True",
    "not False",
    "True and False or True",
    "True and (False or True)",
    "True and False or False",
    "True and (False or False)",
    "True or False and True",
    "(True or False) and True",
    "True or False and False",
    "(True or False) and False",
    "True or True and True",
    "True or True and False",
    "(True or True) and False",
    "True or True or True",
    "True or True or False",
    "True or False or True",
    "True or False or False",
    "False or True or True",
    "False or True or False",
    "False or False or True",
    "False or False or False",
    "True and True and True",
    "True and True and False",
    "True and False and True",
    "True and False and False",
    "False and True and True",
    #
    # Bitwise ops
    #
    "1 | 2",
    "1 & 2",
    "1 ^ 2",
    "1 << 2",
    "1 >> 2",
    #
    # Comparison ops
    #
    "1 == 2",
    "1 != 2",
    "1 < 2",
    "1 <= 2",
    "1 > 2",
    "1 >= 2",
    "1 < 2 < 3",
    "1 < 3 < 2",
    "3 > 2 > 1",
    "1 > 3 > 2",
    #
    # Constructors
    #
    "bool('')",
    "bool('a')",
    "bool(0)",
    "bool(0.0)",
    "bool(1)",
    "bool(1.0)",
    "bool([1])",
    "bool([])",
    "dict()",
    "float('1.0')",
    "int('1')",
    "int(1)",
    "list((1, 2))",
    "list((1,))",
    "list()",
    "list([1])",
    "str()",
    "str(1)",
    "tuple((1, 2))",
    "tuple((1,))",
    "tuple()",
    "tuple([1])",
    # Tuple is translated to array.
    # "tuple()",
    #
    # Other builtin functions
    #
    "chr(35)",
    "ord('a')",
    "len('abc')",
    "len([1, 2])",
    "len([])",
    "max([1, 2])",
    "min([1, 2])",
    "list(range(1))",
    "list(range(0, 1))",
    "list(range(0, 10, 2))",
    "sorted([2, 1])",
    #
    # Functions from stdlib
    #
    "list(reversed([1, 2]))",
    "sorted([0, 4, 3, 1, 2])",
    "list(enumerate(['a', 'b', 'c']))",
    "list(zip([1, 2, 3], ['a', 'b', 'c']))",
    "[1, 2] == sorted([2, 1])",
    # "[3, 2, 1] == sorted([2, 3, 1], reverse=True)",
    #
    # More builtin functions
    #
    "abs(-1)",
    "abs(1)",
    # "aiter()",
    "all([])",
    "all([True, False])",
    "all([True, True])",
    "all([False, False])",
    # "anext()",
    "any([])",
    "any([True, False])",
    "any([True, True])",
    "any([False, False])",
    # "ascii()",
    # "bin()",
    # "bytearray()",
    # "bytes()",
    # "callable()",
    # "chr()",
    # "complex()",
    # "delattr()",
    # "dict()",
    # "dir()",
    # "divmod()",
    # "enumerate()",
    # "eval()",
    # "exec()",
    # "exit()",
    # "filter()",
    # "float()",
    # "format()",
    # "frozenset()",
    # "getattr()",
    # "globals()",
    # "hasattr()",
    # "hash()",
    # "help()",
    # "hex()",
    # "id()",
    # "input()",
    # "isinstance()",
    # "issubclass()",
    # "iter()",
    # "len()",
    "len([1, 2])",
    "len([])",
    "len('abc')",
    # "map()",
    # "max()",
    "max([1, 2])",
    # "min()",
    "min([1, 2])",
    # "oct()",
    # "ord()",
    # "pow()",
    "pow(2, 3)",
    # "range()",
    # "repr()",
    # "reversed()",
    "list(reversed([1, 2]))",
    # "round()",
    "round(1.0)",
    "round(1.1)",
    "round(1.5)",
    # "slice()",
    # "sum()",
    "sum([1, 2])",
    "sum([])",
    # "super()",
    # "type()",
    # "vars()",
    # "zip()",
    "list(zip([1], [2]))",
    #
    # Lambda
    # "(lambda x: x)(3)",
    #
    # List and tuples expressions
    #
    "[]",
    "[1]",
    "[1, 2]",
    "[1, 2] == [1, 2]",
    "[1, 2] == [2, 1]",
    "[1, 2] == list([1, 2])",
    #
    # List and tuples via generators
    #
    # "[x for x in [1, 2]]",
    # "[x for x in (1, 2)]",
    # "{k: k for k in 'abc'}",
    #
    # Str function / constructor
    #
    "str(True).lower()",
    "str(False).lower()",
    "str([])",
    "str([1])",
    "str([1, 2, 'a', -1])",
    # "str(1.0)",
    # "str(1.0) == '1.'",
    # "str(1e3) == '1000.'",
    #
    # Str
    #
    # "'a'.upper()",
    # "'a'.lower()",
    # "'a'.capitalize()",
    # "'a'.title()",
    # "'a'.swapcase()",
    # "'a'.isupper()",
    # "'a'.islower()",
    # "'a'.istitle()",
    # "'a'.isalpha()",
    # "'a'.isalnum()",
    # "'a'.isdigit()",
    # "'a'.isspace()",
    # "'a'.isprintable()",
    # "'a'.isdecimal()",
    # "'a'.encode()",
    # "'abc'.startswith('a')",
    # "'abc'.startswith('b')",
    # "'abc'.endswith('c')",
    # "'abc'.endswith('b')",
    # "'abc'.find('a')",
    # "'abc'.find('b')",
    # "'abc'.find('c')",
    # "'abc'.find('d')",
    # "'abc'.rfind('a')",
    # "'abc'.rfind('b')",
    # "'abc'.rfind('c')",
    # "'abc'.rfind('d')",
    # "'abc'.index('a')",
    # "'abc'.index('b')",
    # "'abc'.index('c')",
    # "'abc'.rindex('a')",
    # "'abc'.rindex('b')",
    # "'abc'.rindex('c')",
    # "'abc'.count('a')",
    # "'abc'.count('b')",
    # "'abc'.count('c')",
    # "'abc'.count('d')",
    # "'abc'.replace('a', 'b')",
    # "str(True) == 'True'",
    # "str(False) == 'False'",
    # Tupes (nope)
    # "(1, 2)",
    # Set expressions (nope)
    # "1 in {1}",
    # "1 not in {1}",
    # "{1, 2} == {2, 1}",
    #
    #
    # Dicts + dict methods
    #
    "{}",
    "{'a': 1}",
    "dict(a=1)",
    "dict([('a', 1)])",
    "list({'a': 1})",
    "list({'a': 1}.keys())",
    "list({'a': 1}.values())",
    "{'a': 1} == {'a': 1}",
    "dict(a=1) == {'a': 1}",
    "dict([('a', 1)]) == {'a': 1}",
    #
    # Subscripts
    #
    "[1][0] == 1",
    "{'a': 1}['a']",
    # Fail
    # "{1: 1}",
    # "list({'a': 1}.items())",
    # Ellipsis
    # "str(...) == 'Ellipsis'",
    #
    # Equality
    #
    "1 == 1",
    "1 != 0",
    "dict() == {}",
    "list() == []",
    "tuple() == ()",
    # "set() == set()",
    "list([1, 2]) == [1, 2]",
    "tuple([1, 2]) == (1, 2)",
    # "set([1, 2]) == {1, 2}",
    #
    # Strings methods
    #
    "'Ab+'.lower()",
    "'Ab+'.upper()",
    #
    # In expressions
    #
    "'a' in 'abc'",
    "'a' in ('a', 'b')",
    "'a' in ['a', 'b']",
    "'a' not in 'abc'",
    "'a' not in ('a', 'b')",
    "'a' not in ['a', 'b']",
    "1 in (1, 2)",
    "1 in [1, 2]",
    "1 in {1: 1}",
    "1 not in (1, 2)",
    "1 not in [1, 2]",
    "1 not in {1: 1}",
    #
    # If expressions
    #
    "1 if True else 2",
    "1 if False else 2",
    #
    # String formatting
    #
    # "f'a'",
    # '"%d" % 1',
]
