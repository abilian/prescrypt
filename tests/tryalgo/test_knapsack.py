import pytest

from tests.tryalgo.utils import check

EXAMPLES = [
    ([580, 1616, 1906, 1942, 50, 294], [874, 620, 345, 269, 360, 470], 2000, 1704),
    ([2, 3, 5], [6, 4, 2], 9, 10),
    ([5, 4, 3, 2, 1], [30, 19, 20, 10, 20], 10, 70),
    ([3, 3, 2, 2, 2], [40, 40, 10, 20, 30], 7, 90),
    ([2], [42], 1, 0),
    # ([], [], 0, 0),
    ([1], [42], 0, 0),
]


@pytest.mark.parametrize("p, v, cmax, opt", EXAMPLES)
def test_knapsack(p, v, cmax, opt):
    kp1 = f"knapsack({p}, {v}, {cmax})[0]"
    check("knapsack", kp1, opt)

    # FIXME: knapsack2 is not working
    # kp2 = f"knapsack2({p}, {v}, {cmax})[0]"
    # check("knapsack", kp2, opt)

    # expr = f"{kp1} == {kp2} == {opt}"
    # check("knapsack", expr, True)
