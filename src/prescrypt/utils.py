import json
import re


def unify(x):
    """Turn string or list of strings parts into string.

    Braces are placed around it if it's not alphanumerical
    """
    # Note that r'[\.\w]' matches anyting in 'ab_01.äé'

    if isinstance(x, (tuple, list)):
        x = "".join(x)

    if x[0] in "'\"" and x[0] == x[-1] and x.count(x[0]) == 2:
        return x  # string
    elif re.match(r"^[.\w]*$", x, re.UNICODE):
        return x  # words consisting of normal chars, numbers and dots
    elif re.match(r"^[.\w]*\(.*\)$", x, re.UNICODE) and x.count(")") == 1:
        return x  # function calls (e.g. 'super()' or 'foo.bar(...)')
    elif re.match(r"^[.\w]*\[.*]$", x, re.UNICODE) and x.count("]") == 1:
        return x  # indexing
    elif re.match(r"^\{.*}$", x, re.UNICODE) and x.count("}") == 1:
        return x  # dicts
    else:
        return f"({x})"


def js_repr(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)


def flatten(js_code: list | str) -> str:
    """Flatten a list of strings or a single string to a single string."""
    match js_code:
        case str(s):
            return s
        case [*x]:
            return "".join(flatten(s) for s in x)
        case _:
            raise ValueError(f"Unexpected type: {type(js_code)}")
