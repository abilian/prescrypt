"""Golden test for three partition algorithm."""
from __future__ import annotations


# --- Three partition function (from three_partition.py) ---

def three_partition(x):
    """partition a set of integers in 3 parts of same total value

    :param x: table of nonnegative values
    :returns: triplet of the integers encoding the sets, or None otherwise
    :complexity: O(2^{2n})
    """
    f = [0] * (1 << len(x))
    for i, _ in enumerate(x):
        for S in range(1 << i):
            f[S | (1 << i)] = f[S] + x[i]
    for A in range(1 << len(x)):
        for B in range(1 << len(x)):
            if A & B == 0 and f[A] == f[B] and 3 * f[A] == f[-1]:
                return A, B, ((1 << len(x)) - 1) ^ A ^ B
    return None


# --- Tests ---

# Test case 1: Partitionable set
x1 = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # Sum is 45, each part should sum to 15
result1 = three_partition(x1)
if result1 is not None:
    A, B, C = result1
    # Verify each partition sums to same value
    sum_a = sum(x1[i] for i in range(len(x1)) if A & (1 << i))
    sum_b = sum(x1[i] for i in range(len(x1)) if B & (1 << i))
    sum_c = sum(x1[i] for i in range(len(x1)) if C & (1 << i))
    print(f"partition sums: {sum_a}, {sum_b}, {sum_c}")
    print(f"all equal: {str(sum_a == sum_b == sum_c)}")
else:
    print("partition sums: None")
    print("all equal: False")

# Test case 2: Simple partitionable set
x2 = [1, 1, 1, 2, 2, 2, 3, 3, 3]  # Sum is 18, each part should sum to 6
result2 = three_partition(x2)
print(f"partition exists: {str(result2 is not None)}")

# Test case 3: Non-partitionable set (sum not divisible by 3)
x3 = [1, 2, 3, 4]  # Sum is 10, not divisible by 3
result3 = three_partition(x3)
print(f"non-partitionable: {str(result3 is None)}")

print("three_partition tests passed")
