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
