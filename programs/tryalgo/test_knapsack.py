"""Golden test for knapsack algorithm."""
from __future__ import annotations


# --- Knapsack function (from knapsack.py) ---

def knapsack(p, v, cmax):
    """Knapsack problem: select maximum value set of items if total size not
    more than capacity

    :param p: table with size of items
    :param v: table with value of items
    :param cmax: capacity of bag
    :requires: number of items non-zero
    :returns: value optimal solution, list of item indexes in solution
    :complexity: O(n * cmax), for n = number of items
    """
    n = len(p)
    opt = [[0] * (cmax + 1) for _ in range(n + 1)]
    sel = [[False] * (cmax + 1) for _ in range(n + 1)]
    #                               --- basic case
    for cap in range(p[0], cmax + 1):
        opt[0][cap] = v[0]
        sel[0][cap] = True
    #                               --- induction case
    for i in range(1, n):
        for cap in range(cmax + 1):
            if cap >= p[i] and opt[i-1][cap - p[i]] + v[i] > opt[i-1][cap]:
                opt[i][cap] = opt[i-1][cap - p[i]] + v[i]
                sel[i][cap] = True
            else:
                opt[i][cap] = opt[i-1][cap]
                sel[i][cap] = False
    #                               --- reading solution
    cap = cmax
    solution = []
    for i in range(n-1, -1, -1):
        if sel[i][cap]:
            solution.append(i)
            cap -= p[i]
    return (opt[n - 1][cmax], solution)


# --- Tests ---

# Test case 1: Simple case
weights1 = [2, 3, 5]
values1 = [6, 4, 2]
capacity1 = 9
opt1, items1 = knapsack(weights1, values1, capacity1)
print(f"knapsack1: {opt1}")  # Should be 10

# Test case 2: Larger case
weights2 = [5, 4, 3, 2, 1]
values2 = [30, 19, 20, 10, 20]
capacity2 = 10
opt2, items2 = knapsack(weights2, values2, capacity2)
print(f"knapsack2: {opt2}")  # Should be 70

# Test case 3: Another case
weights3 = [3, 3, 2, 2, 2]
values3 = [40, 40, 10, 20, 30]
capacity3 = 7
opt3, items3 = knapsack(weights3, values3, capacity3)
print(f"knapsack3: {opt3}")  # Should be 90

# Test case 4: Item doesn't fit
weights4 = [2]
values4 = [42]
capacity4 = 1
opt4, items4 = knapsack(weights4, values4, capacity4)
print(f"knapsack4: {opt4}")  # Should be 0

# Test case 5: Zero capacity
weights5 = [1]
values5 = [42]
capacity5 = 0
opt5, items5 = knapsack(weights5, values5, capacity5)
print(f"knapsack5: {opt5}")  # Should be 0

print("knapsack tests passed")
