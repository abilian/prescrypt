"""Golden test for fast exponentiation (modular power)."""
from __future__ import annotations


# --- Fast exponentiation functions (from fast_exponentiation.py) ---

def fast_exponentiation(a, b, q):
    """Compute (a pow b) % q

    :param int a b: non negative
    :param int q: positive
    :complexity: O(log b)
    """
    assert a >= 0 and b >= 0 and q >= 1
    result = 1
    while b:
        if b % 2 == 1:
            result = (result * a) % q
        a = (a * a) % q
        b >>= 1
    return result


# --- Tests ---

# Test basic cases
result1 = fast_exponentiation(2, 10, 1000)
print(f"pow(2, 10, 1000): {result1}")  # 2^10 = 1024, 1024 % 1000 = 24

result2 = fast_exponentiation(3, 5, 100)
print(f"pow(3, 5, 100): {result2}")  # 3^5 = 243, 243 % 100 = 43

result3 = fast_exponentiation(7, 3, 13)
print(f"pow(7, 3, 13): {result3}")  # 7^3 = 343, 343 % 13 = 5

# Test edge cases
result4 = fast_exponentiation(5, 0, 10)
print(f"pow(5, 0, 10): {result4}")  # Any^0 = 1

result5 = fast_exponentiation(0, 5, 10)
print(f"pow(0, 5, 10): {result5}")  # 0^5 = 0

result6 = fast_exponentiation(10, 1, 7)
print(f"pow(10, 1, 7): {result6}")  # 10 % 7 = 3

# Test medium exponents (within JS safe integer range)
result7 = fast_exponentiation(2, 30, 1000)
print(f"pow(2, 30, mod): {result7}")  # 2^30 = 1073741824, mod 1000 = 824

result8 = fast_exponentiation(3, 20, 10000)
print(f"pow(3, 20, mod): {result8}")  # 3^20 mod 10000 = 6561

# Test Fermat's little theorem: a^(p-1) = 1 (mod p) for prime p
# 2^6 % 7 = 64 % 7 = 1
result9 = fast_exponentiation(2, 6, 7)
print(f"fermat(2, 6, 7): {result9}")  # Should be 1

# 3^10 % 11 = 1
result10 = fast_exponentiation(3, 10, 11)
print(f"fermat(3, 10, 11): {result10}")  # Should be 1

print("fast_exponentiation tests passed")
