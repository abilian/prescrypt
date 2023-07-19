import heapq
import random

from prescrypt import evalpy

GRAMMAR = {
    "<expr>": [
        ["<term>"],
        ["<term>", "+", "<expr>"],
        ["<term>", "-", "<expr>"],
    ],
    "<term>": [
        ["<fact>"],
        ["<fact>", "*", "<term>"],
        ["<fact>", "/", "<term>"],
        # ['<fact>', '//', '<term>'],
        # ['<fact>', '%', '<term>'],
    ],
    "<fact>": [
        lambda: random.randint(-1000, 1000),
        lambda: random.choice("abceedfg"),
        ["(", "<expr>", ")"],
        # ['str(', '<expr>', ')'],
        ["int(", "<expr>", ")"],
        # ['float(', '<expr>', ')'],
        # ['bool(', '<expr>', ')'],
    ],
}


def is_terminal(s):
    for sym in s:
        if sym.startswith("<"):
            return False
    return True


def gen(grammar: dict):
    q = [(1, ["<expr>"])]
    n = 0
    while True:
        _, s = heapq.heappop(q)

        a = []
        b = s.copy()
        while b:
            sym = b.pop(0)
            if sym.startswith("<"):
                for rhs in grammar[sym]:
                    s_new = a.copy()
                    if callable(rhs):
                        rhs = str(rhs())
                        s_new.append(rhs)
                    s_new.extend(rhs)
                    s_new.extend(b)
                    if is_terminal(s_new):
                        yield "".join(s_new)
                        n += 1
                    else:
                        heapq.heappush(q, (len(s_new), s_new))
                break  # only generate leftmost derivations
            a.append(sym)


def test_gen():
    for i, expr in enumerate(gen(GRAMMAR)):
        if i > 1000:
            break
        try:
            py_result = eval(expr)
        except Exception as e:
            continue

        js_result = evalpy(expr)
        assert py_result == js_result, f"{expr} = {py_result} != {js_result}"
