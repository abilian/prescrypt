EXPRESSIONS1 = [
    # Literals
    "1",
    "1.0",
    "1e3",
    "1e-3",
    "True",
    "False",
    "'a'",
    '"a"',
    "f'a'",
    # Arithmetic
    "1+1",
    "2 * 3 + 5 * 6",
    "'a' + 'b'",
    "3 * 'a'",
    '"a" + "b"',
    "1 // 2",
    "1 % 2",
    # Constructors
    "str()",
    "str(1)",
    "int(1)",
    "int('1')",
    "float('1.0')",
    "bool(1)",
    "bool(0)",
    "bool(1.0)",
    "bool(0.0)",
    "bool('a')",
    "bool('')",
    "bool([1])",
    "bool([])",
    "list()",
    "list([1])",
    "list((1,))",
    "list((1, 2))",
    "tuple()",
    "tuple([1])",
    "tuple((1,))",
    "tuple((1, 2))",
    "dict()",
    # Tuple is translated to array.
    # "tuple()",
    # Other builtin functions
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
    # Lambda
    "(lambda x: x)(3)",
    # Boolean expressions
    "True or False",
    "True and False",
    # Bitwise expressions
    "1 | 2",
    "1 & 2",
    "1 ^ 2",
    "1 << 2",
    "1 >> 2",
    # Comparison expressions
    "1 == 2",
    "1 != 2",
    "1 < 2",
    "1 <= 2",
    "1 > 2",
    "1 >= 2",
    # In expressions
    "1 in [1, 2]",
    "1 not in [1, 2]",
    "1 in (1, 2)",
    "1 not in (1, 2)",
    "1 in {1: 1}",
    "1 not in {1: 1}",
    "'a' in 'abc'",
    "'a' not in 'abc'",
    "'a' in ['a', 'b']",
    "'a' not in ['a', 'b']",
    "'a' in ('a', 'b')",
    "'a' not in ('a', 'b')",
    # If expressions
    "1 if True else 2",
    "1 if False else 2",
    # List and tuples expressions
    "[]",
    "[1]",
    "[1, 2]",
    # List and tuples via generators
    # "[x for x in [1, 2]]",
    # "[x for x in (1, 2)]",
    # "{k: k for k in 'abc'}",
    #
    # Str function / constructor
    #
    "str(1.0) == '1.'",
    "str(1e3) == '1000.'",
    # Lists
    # Str (nope)
    "str(True).lower()",
    "str(False).lower()",
    # "str(True) == 'True'",
    # "str(False) == 'False'",
    # Tupes (nope)
    # "(1, 2)",
    # Set expressions (nope)
    # "1 in {1}",
    # "1 not in {1}",
    # "{1, 2} == {2, 1}",
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
    "%d" % 1,
    # Equality
    "1 == 1",
    "1 != 0",
    # "dict() == {}",
    # "list() == []",
    # "tuple() == ()",
    # "set() == set()",
    # "list([1, 2]) == [1, 2]",
    # "tuple([1, 2]) == (1, 2)",
    # "set([1, 2]) == {1, 2}",
    #
    # Strings
    #
    "'Ab+'.lower()",
    "'Ab+'.upper()",
    #
    # Functions from stdlib
    #
    "list(reversed([1, 2]))",
    "sorted([0, 4, 3, 1, 2])",
    "list(enumerate(['a', 'b', 'c']))",
    "list(zip([1, 2, 3], ['a', 'b', 'c']))",
]

# TODO: merge
EXPRESSIONS2 = [
    # Literals
    "1",
    "1.0",
    "1e3",
    "1e-3",
    "True",
    "False",
    "'a'",
    '"a"',
    "f'a'",
    # Arithmetic
    "1+1",
    "2 * 3 + 5 * 6",
    "'a' + 'b'",
    "3 * 'a'",
    '"a" + "b"',
    "1 // 2",
    "1 % 2",
    # Constructors
    "str(1)",
    "int('1')",
    "float('1.0')",
    "bool(1)",
    "bool(0)",
    "bool(1.0)",
    "bool(0.0)",
    "bool('a')",
    "bool('')",
    "bool([1])",
    "bool([])",
    # Lambda
    "(lambda x: x)(3)",
    # Boolean expressions
    "True or False",
    "True and False",
    # Bitwise expressions
    "1 | 2",
    "1 & 2",
    "1 ^ 2",
    "1 << 2",
    "1 >> 2",
    # Comparison expressions
    "1 == 2",
    "1 != 2",
    "1 < 2",
    "1 <= 2",
    "1 > 2",
    "1 >= 2",
    # In expressions
    "1 in [1, 2]",
    "1 not in [1, 2]",
    "1 in (1, 2)",
    "1 not in (1, 2)",
    "1 in {1: 1}",
    "1 not in {1: 1}",
    "'a' in 'abc'",
    "'a' not in 'abc'",
    "'a' in ['a', 'b']",
    "'a' not in ['a', 'b']",
    "'a' in ('a', 'b')",
    "'a' not in ('a', 'b')",
    # If expressions
    "1 if True else 2",
    "1 if False else 2",
    # List and tuples expressions
    "[1, 2] == [2, 1]",
    "[1, 2] == list([1, 2])",
    "[1, 2] == [x for x in [1, 2]]",
    "[1, 2] == [x for x in (1, 2)]",
    "[1, 2] == sorted([2, 1])",
    # "{k: k for k in 'abc'}",
    # Str
    "str(1.0) == '1.'",
    "str(1e3) == '1000.'",
    # Lists
    "[]",
    "[1]",
    "[1, 2]",
    # Str (nope)
    # "str(True)",
    # "str(False)",
    # "str(True) == 'True'",
    # "str(False) == 'False'",
    # Tupes (nope)
    # "(1, 2)",
    # Set expressions (nope)
    # "1 in {1}",
    # "1 not in {1}",
    # "{1, 2} == {2, 1}",
    # Dict
    "{}",
    "{'a': 1}",
    "list({'a': 1})",
    "list({'a': 1}.keys())",
    "list({'a': 1}.values())",
    "{'a': 1} == {'a': 1}",
    "dict(a=1) == {'a': 1}",
    "dict([('a', 1)]) == {'a': 1}",
    # Fail
    # "{1: 1}",
    # "list({'a': 1}.items())",
    # Ellipsis
    # "str(...) == 'Ellipsis'",
    '"%d" % 1',
]

EXPRESSIONS = EXPRESSIONS1 + EXPRESSIONS2
