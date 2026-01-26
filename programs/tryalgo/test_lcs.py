"""Golden test for Longest Common Subsequence."""
from __future__ import annotations


# --- LCS function (from longest_common_subsequence.py) ---

def longest_common_subsequence(x, y):
    """Longest common subsequence

    Dynamic programming

    :param x:
    :param y: x, y are lists or strings
    :returns: longest common subsequence in form of a string
    :complexity: `O(|x|*|y|)`
    """
    n = len(x)
    m = len(y)

    # Compute optimal length
    A = [[0 for j in range(m + 1)] for i in range(n + 1)]
    for i in range(n):
        for j in range(m):
            if x[i] == y[j]:
                A[i + 1][j + 1] = A[i][j] + 1
            else:
                A[i + 1][j + 1] = max(A[i][j + 1], A[i + 1][j])

    # Extract solution in reverse order
    sol = []
    i = n
    j = m
    while A[i][j] > 0:
        if A[i][j] == A[i - 1][j]:
            i -= 1
        elif A[i][j] == A[i][j - 1]:
            j -= 1
        else:
            i -= 1
            j -= 1
            sol.append(x[i])
    return ''.join(sol[::-1])


# --- Tests ---

# Test basic LCS
result1 = longest_common_subsequence("ABCDGH", "AEDFHR")
print(f"lcs(ABCDGH, AEDFHR): {result1}")  # Should be "ADH"

result2 = longest_common_subsequence("AGGTAB", "GXTXAYB")
print(f"lcs(AGGTAB, GXTXAYB): {result2}")  # Should be "GTAB"

# Test identical strings
result3 = longest_common_subsequence("hello", "hello")
print(f"lcs(hello, hello): {result3}")  # Should be "hello"

# Test no common characters
result4 = longest_common_subsequence("abc", "xyz")
print(f"lcs(abc, xyz): {result4}")  # Should be ""

# Test one empty string
result5 = longest_common_subsequence("abc", "")
print(f"lcs(abc, ''): {result5}")  # Should be ""

result6 = longest_common_subsequence("", "xyz")
print(f"lcs('', xyz): {result6}")  # Should be ""

# Test single character
result7 = longest_common_subsequence("a", "a")
print(f"lcs(a, a): {result7}")  # Should be "a"

result8 = longest_common_subsequence("a", "b")
print(f"lcs(a, b): {result8}")  # Should be ""

# Test subsequence vs substring
result9 = longest_common_subsequence("XMJYAUZ", "MZJAWXU")
print(f"lcs(XMJYAUZ, MZJAWXU): {result9}")  # Should be "MJAU"

print("lcs tests passed")
