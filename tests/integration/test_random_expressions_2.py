from prescrypt import evalpy

from .util import gen_expr


def test_gen():
    for i in range(0, 100):
        expr = gen_expr()

        try:
            py_result = eval(expr)
        except Exception:
            continue

        js_result = evalpy(expr)
        assert js_equals(py_result, js_result)


def to_js(x):
    if x is None:
        return "null"

    if isinstance(x, bool):
        return str(x).lower()

    if isinstance(x, (int, float)):
        return str(float(x))

    if isinstance(x, (list, tuple)):
        return tuple(to_js(y) for y in x)

    if isinstance(x, dict):
        return {to_js(k): to_js(v) for k, v in x.items()}

    if isinstance(x, str):
        try:
            int(x)
        except ValueError:
            pass
        try:
            return float(x)
        except ValueError:
            pass

    return x


#
# Note: we're using a very liberal definition of equality here.
#
def js_equals(x, y):
    x = to_js(x)
    y = to_js(y)

    if x is None and y == 0.0:
        return True
    if y is None and x == 0.0:
        return True

    if isinstance(x, tuple) and isinstance(y, tuple):
        if len(x) != len(y):
            return False
        return all(js_equals(a, b) for a, b in zip(x, y))

    # JS dict keys are always strings
    if isinstance(x, dict) and isinstance(y, dict):
        x_keys = tuple(x.keys())
        y_keys = tuple(y.keys())
        x_values = tuple(x.values())
        y_values = tuple(y.values())
        return js_equals(x_keys, y_keys) and js_equals(x_values, y_values)

    return x == y
