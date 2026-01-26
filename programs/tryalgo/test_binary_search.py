"""Golden test for binary search algorithms."""
from __future__ import annotations


# --- Binary search functions (from binary_search.py) ---

def discrete_binary_search(tab, lo, hi):
    """Binary search in a table of booleans

    :param tab: table of n values [False, ..., False, True, ..., True]
    :param int lo: first index
    :param int hi: last index
    :requires: tab[lo] = False and tab[hi] = True
    :returns: first index with True
    :complexity: O(log(hi - lo))
    """
    while hi - lo > 1:
        mid = lo + (hi - lo) // 2
        if tab[mid]:
            hi = mid
        else:
            lo = mid
    return hi


def continuous_binary_search(f, lo, hi, gap=1e-4):
    """Binary search for a function changing from False to True

    :param f: function from float to bool [False, ..., False, True, ..., True]
    :param float lo: lower bound
    :param float hi: upper bound
    :param float gap: maximal margin error
    :requires: f(lo) = False and f(hi) = True
    :returns: value x such that f(x - gap) = False and f(x + gap) = True
    :complexity: O(log((hi - lo) / gap))
    """
    while hi - lo > gap:
        mid = (lo + hi) / 2.0
        if f(mid):
            hi = mid
        else:
            lo = mid
    return lo


# --- Tests ---

# Test discrete binary search
# Find first True in a boolean table
tab = [False, False, False, True, True, True, True, True]
result = discrete_binary_search(tab, 0, len(tab) - 1)
print(f"discrete_binary_search: {result}")  # Should be 3

# Another test case
tab2 = [False, False, False, False, False, True]
result2 = discrete_binary_search(tab2, 0, len(tab2) - 1)
print(f"discrete_binary_search2: {result2}")  # Should be 5

# Test continuous binary search
# Find x where x^2 >= 2 (sqrt(2) ~ 1.414)
def f(x):
    return x * x >= 2

result3 = continuous_binary_search(f, 0, 2, gap=0.01)
# Result should be close to 1.41
print(f"continuous_binary_search: {int(result3 * 100)}")  # ~141

print("binary_search tests passed")
