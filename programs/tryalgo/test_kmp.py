"""Golden test for Knuth-Morris-Pratt string matching."""
from __future__ import annotations


# --- KMP functions (from knuth_morris_pratt.py) ---

def maximum_border_length(w):
    """Maximum string borders by Knuth-Morris-Pratt

    :param w: string
    :returns: table f such that f[i] is the longest border length of w[:i + 1]
    :complexity: linear
    """
    n = len(w)
    f = [0] * n                # init f[0] = 0
    k = 0                      # current longest border length
    for i in range(1, n):      # compute f[i]
        while w[k] != w[i] and k > 0:
            k = f[k - 1]       # mismatch: try the next border
        if w[k] == w[i]:       # last characters match
            k += 1             # we can increment the border length
        f[i] = k               # we found the maximal border of w[:i + 1]
    return f


def knuth_morris_pratt(s, t):
    """Find a substring by Knuth-Morris-Pratt

    :param s: the haystack string
    :param t: the needle string
    :returns: index i such that s[i: i + len(t)] == t, or -1
    :complexity: O(len(s) + len(t))
    """
    sep = '\x00'                   # special unused character
    assert sep not in t and sep not in s
    f = maximum_border_length(t + sep + s)
    n = len(t)
    for i, fi in enumerate(f):
        if fi == n:                # found a border of the length of t
            return i - 2 * n       # beginning of the border in s
    return -1


def powerstring_by_border(u):
    """Power string by Knuth-Morris-Pratt

    :param u: string
    :returns: largest k such that there is a string y with u = y^k
    :complexity: O(len(u))
    """
    f = maximum_border_length(u)
    n = len(u)
    if n % (n - f[-1]) == 0:       # does the alignment shift divide n ?
        return n // (n - f[-1])    # we found a power decomposition
    return 1


# --- Tests ---

# Test maximum_border_length
borders = maximum_border_length("abacaba")
print(f"borders(abacaba): {' '.join(str(x) for x in borders)}")  # 0 0 1 0 1 2 3

borders2 = maximum_border_length("aaaa")
print(f"borders(aaaa): {' '.join(str(x) for x in borders2)}")  # 0 1 2 3

# Test knuth_morris_pratt - find substring
result1 = knuth_morris_pratt("hello world", "world")
print(f"kmp(hello world, world): {result1}")  # Should be 6

result2 = knuth_morris_pratt("abcabcabc", "abc")
print(f"kmp(abcabcabc, abc): {result2}")  # Should be 0

result3 = knuth_morris_pratt("hello world", "xyz")
print(f"kmp(hello world, xyz): {result3}")  # Should be -1

result4 = knuth_morris_pratt("aaaaa", "aa")
print(f"kmp(aaaaa, aa): {result4}")  # Should be 0

result5 = knuth_morris_pratt("mississippi", "issi")
print(f"kmp(mississippi, issi): {result5}")  # Should be 1

# Test powerstring_by_border
power1 = powerstring_by_border("abcabc")
print(f"power(abcabc): {power1}")  # Should be 2

power2 = powerstring_by_border("abcabcabc")
print(f"power(abcabcabc): {power2}")  # Should be 3

power3 = powerstring_by_border("abcd")
print(f"power(abcd): {power3}")  # Should be 1

power4 = powerstring_by_border("aaaa")
print(f"power(aaaa): {power4}")  # Should be 4

print("kmp tests passed")
