import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Union

import quickjs

JSON = Union[str, int, float, bool, None, List[Any], Dict[str, Any]]


#
# Useful for code that involve JS evaluation
#
def js_eval(code) -> JSON:
    # _pre_check(code)

    ctx = quickjs.Context()
    result = ctx.eval(code)
    if isinstance(result, quickjs.Object):
        return _to_json(result)
    return result


def _to_json(obj: quickjs.Object) -> JSON:
    j = obj.json()
    return json.loads(j)


def _pre_check(x):
    tmp_file = Path(tempfile.mktemp(suffix=".js", prefix="prescrypt_"))
    tmp_file.write_text(x)
    try:
        subprocess.run(["node", str(tmp_file)], check=True)
        tmp_file.unlink()
    except subprocess.CalledProcessError as e:
        print(e.stdout)
        print(tmp_file)
        raise


#
# Note: we're using a very liberal definition of equality here.
#
def js_equals(x, y):
    x = _to_js(x)
    y = _to_js(y)

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


js_eq = js_equals


def _to_js(x):
    if x is None:
        return "null"

    if isinstance(x, bool):
        return str(x).lower()

    if isinstance(x, (int, float)):
        return str(float(x))

    if isinstance(x, (list, tuple)):
        return tuple(_to_js(y) for y in x)

    if isinstance(x, dict):
        return {_to_js(k): _to_js(v) for k, v in x.items()}

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
