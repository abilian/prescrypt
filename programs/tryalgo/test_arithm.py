"""Golden test for arithmetic functions."""
from __future__ import annotations


# --- Arithmetic functions (from arithm.py) ---

def pgcd(a, b):
    """Greatest common divisor for a and b"""
    return a if b == 0 else pgcd(b, a % b)


def bezout(a, b):
    """Bezout coefficients for a and b"""
    if b == 0:
        return (1, 0)
    u, v = bezout(b, a % b)
    return (v, u - (a // b) * v)


def inv(a, p):
    """Inverse of a in Z_p"""
    return bezout(a, p)[0] % p


def binom(n, k):
    """Binomial coefficients for n choose k"""
    prod = 1
    for i in range(k):
        prod = (prod * (n - i)) // (i + 1)
    return prod


def binom_modulo(n, k, p):
    """Binomial coefficients for n choose k, modulo p"""
    prod = 1
    for i in range(k):
        prod = (prod * (n - i) * inv(i + 1, p)) % p
    return prod


# --- Tests ---

# Test GCD
result1 = pgcd(12, 18)
print(f"pgcd(12, 18): {result1}")  # Should be 6

result2 = pgcd(48, 18)
print(f"pgcd(48, 18): {result2}")  # Should be 6

result3 = pgcd(17, 13)
print(f"pgcd(17, 13): {result3}")  # Should be 1

# Test binomial coefficient
result4 = binom(4, 2)
print(f"binom(4, 2): {result4}")  # Should be 6

result5 = binom(10, 3)
print(f"binom(10, 3): {result5}")  # Should be 120

result6 = binom(5, 0)
print(f"binom(5, 0): {result6}")  # Should be 1

# Test modular inverse
result7 = inv(8, 17)
print(f"inv(8, 17): {result7}")  # Should be 15 (since 8*15 mod 17 = 1)

result8 = inv(3, 7)
print(f"inv(3, 7): {result8}")  # Should be 5 (since 3*5 mod 7 = 1)

# Test binomial modulo
result9 = binom_modulo(5, 2, 3)
print(f"binom_modulo(5, 2, 3): {result9}")  # Should be 1 (10 mod 3 = 1)

result10 = binom_modulo(10, 3, 7)
print(f"binom_modulo(10, 3, 7): {result10}")  # Should be 1 (120 mod 7 = 1)

print("arithm tests passed")
