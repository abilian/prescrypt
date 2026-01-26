"""Golden test for Longest Increasing Subsequence."""
from __future__ import annotations


# --- LIS function (O(n^2) version without bisect) ---

def longest_increasing_subsequence(x):
    """Longest increasing subsequence

    :param x: sequence of comparable elements
    :returns: longest strictly increasing subsequence
    :complexity: O(n^2)
    """
    n = len(x)
    if n == 0:
        return []

    # dp[i] = length of LIS ending at index i
    dp = [1] * n
    # parent[i] = index of previous element in LIS ending at i
    parent = [-1] * n

    for i in range(1, n):
        for j in range(i):
            if x[j] < x[i] and dp[j] + 1 > dp[i]:
                dp[i] = dp[j] + 1
                parent[i] = j

    # Find the index with maximum LIS length
    max_len = 0
    max_idx = 0
    for i in range(n):
        if dp[i] > max_len:
            max_len = dp[i]
            max_idx = i

    # Reconstruct the LIS
    result = []
    idx = max_idx
    while idx >= 0:
        result.append(x[idx])
        idx = parent[idx]

    return result[::-1]


# --- Tests ---

# Test basic case
result1 = longest_increasing_subsequence([10, 22, 9, 33, 21, 50, 41, 60, 80])
print(f"lis1: {' '.join(str(x) for x in result1)}")  # 10 22 33 50 60 80 (length 6)
print(f"lis1_len: {len(result1)}")

# Test already sorted
result2 = longest_increasing_subsequence([1, 2, 3, 4, 5])
print(f"lis2: {' '.join(str(x) for x in result2)}")  # 1 2 3 4 5
print(f"lis2_len: {len(result2)}")

# Test reverse sorted
result3 = longest_increasing_subsequence([5, 4, 3, 2, 1])
print(f"lis3: {' '.join(str(x) for x in result3)}")  # Just one element
print(f"lis3_len: {len(result3)}")  # 1

# Test with duplicates (strictly increasing, so duplicates don't extend)
result4 = longest_increasing_subsequence([1, 2, 2, 3, 3, 4])
print(f"lis4: {' '.join(str(x) for x in result4)}")  # 1 2 3 4
print(f"lis4_len: {len(result4)}")

# Test single element
result5 = longest_increasing_subsequence([42])
print(f"lis5: {' '.join(str(x) for x in result5)}")  # 42
print(f"lis5_len: {len(result5)}")

# Test empty
result6 = longest_increasing_subsequence([])
print(f"lis6_len: {len(result6)}")  # 0

# Test classic example
result7 = longest_increasing_subsequence([0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15])
print(f"lis7: {' '.join(str(x) for x in result7)}")  # One possible: 0 2 6 9 11 15 or 0 4 6 9 11 15
print(f"lis7_len: {len(result7)}")  # 6

print("lis tests passed")
