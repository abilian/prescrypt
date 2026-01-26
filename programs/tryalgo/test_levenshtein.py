"""Golden test for Levenshtein edit distance."""
from __future__ import annotations


# --- Levenshtein function (from levenshtein.py) ---

def levenshtein(x, y):
    """Levenshtein edit distance

    :param x:
    :param y: strings
    :returns: distance
    :complexity: O(|x|*|y|)
    """
    n = len(x)
    m = len(y)
    # Create the table A
    A = [[i + j for j in range(m + 1)] for i in range(n + 1)]
    for i in range(n):
        for j in range(m):
            A[i + 1][j + 1] = min(A[i][j + 1] + 1,              # insert
                                  A[i + 1][j] + 1,              # delete
                                  A[i][j] + int(x[i] != y[j]))  # subst.
    return A[n][m]


# --- Tests ---

# Test identical strings
result1 = levenshtein("hello", "hello")
print(f"levenshtein(hello, hello): {result1}")  # Should be 0

# Test one insertion
result2 = levenshtein("cat", "cats")
print(f"levenshtein(cat, cats): {result2}")  # Should be 1

# Test one deletion
result3 = levenshtein("cats", "cat")
print(f"levenshtein(cats, cat): {result3}")  # Should be 1

# Test one substitution
result4 = levenshtein("cat", "bat")
print(f"levenshtein(cat, bat): {result4}")  # Should be 1

# Test multiple edits
result5 = levenshtein("kitten", "sitting")
print(f"levenshtein(kitten, sitting): {result5}")  # Should be 3

# Test completely different strings
result6 = levenshtein("abc", "xyz")
print(f"levenshtein(abc, xyz): {result6}")  # Should be 3

# Test empty string
result7 = levenshtein("", "hello")
print(f"levenshtein('', hello): {result7}")  # Should be 5

result8 = levenshtein("hello", "")
print(f"levenshtein(hello, ''): {result8}")  # Should be 5

# Test classic example
result9 = levenshtein("intention", "execution")
print(f"levenshtein(intention, execution): {result9}")  # Should be 5

print("levenshtein tests passed")
