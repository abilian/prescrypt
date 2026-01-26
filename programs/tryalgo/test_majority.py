"""Golden test for majority element algorithm."""
from __future__ import annotations


# --- Majority function (from majority.py) ---

def majority(L):
    """Majority

    :param L: list of elements
    :returns: element that appears most in L,
             tie breaking with smallest element
    """
    # majority is undefined on the empty set
    if len(L) == 0:
        return None
    count = {}
    for word in L:
        if word in count:
            count[word] += 1
        else:
            count[word] = 1
    # Find element with max count, smallest on tie
    best = None
    best_count = -1
    for word in count:
        c = count[word]
        if c > best_count:
            best = word
            best_count = c
        elif c == best_count and word < best:
            best = word
    return best


# --- Tests ---

# Test clear majority
result1 = majority([1, 2, 1, 1, 3])
print(f"majority([1, 2, 1, 1, 3]): {result1}")  # Should be 1

# Test all same
result2 = majority([5, 5, 5, 5])
print(f"majority([5, 5, 5, 5]): {result2}")  # Should be 5

# Test single element
result3 = majority([42])
print(f"majority([42]): {result3}")  # Should be 42

# Test tie - smallest wins
result4 = majority([1, 2, 1, 2])
print(f"majority([1, 2, 1, 2]): {result4}")  # Should be 1 (tie, smallest wins)

# Test with strings
result5 = majority(["apple", "banana", "apple", "cherry", "apple"])
print(f"majority(fruits): {result5}")  # Should be "apple"

# Test longer list
result6 = majority([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5])
print(f"majority(pi digits): {result6}")  # Should be 5 (appears 3 times)

# Test with negative numbers
result7 = majority([-1, -2, -1, -3, -1])
print(f"majority(negatives): {result7}")  # Should be -1

print("majority tests passed")
