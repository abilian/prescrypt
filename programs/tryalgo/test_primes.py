"""Golden test for prime number algorithms."""
from __future__ import annotations


# --- Prime functions (from primes.py) ---

def eratosthene(n):
    """Prime numbers by sieve of Eratosthene

    :param n: positive integer
    :assumes: n > 2
    :returns: list of prime numbers <n
    :complexity: O(n loglog n)
    """
    P = [True] * n
    answ = [2]
    for i in range(3, n, 2):
        if P[i]:
            answ.append(i)
            for j in range(i * i, n, i):
                P[j] = False
    return answ


def gries_misra(n):
    """Prime numbers by the sieve of Gries-Misra
    Computes both the list of all prime numbers less than n,
    and a table mapping every integer 2 <= x < n to its smallest prime factor

    :param n: positive integer
    :returns: list of prime numbers, and list of prime factors
    :complexity: O(n)
    """
    primes = []
    factor = [0] * n
    for x in range(2, n):
        if not factor[x]:      # no factor found
            factor[x] = x      # meaning x is prime
            primes.append(x)
        for p in primes:       # loop over primes found so far
            if p > factor[x] or p * x >= n:
                break
            factor[p * x] = p  # p is the smallest factor of p * x
    return primes, factor


# --- Tests ---

# Test Eratosthene sieve
primes_e = eratosthene(30)
print(f"eratosthene(30): {repr(primes_e)}")

# Test Gries-Misra sieve
primes_g, factors = gries_misra(30)
print(f"gries_misra(30): {repr(primes_g)}")

# Verify both methods return same primes for several values
check1 = (eratosthene(20) == gries_misra(20)[0])
print(f"check n=20: {str(check1)}")

check2 = (eratosthene(50) == gries_misra(50)[0])
print(f"check n=50: {str(check2)}")

check3 = (eratosthene(100) == gries_misra(100)[0])
print(f"check n=100: {str(check3)}")

# Verify all checks pass
all_check = all([
    eratosthene(n) == gries_misra(n)[0]
    for n in range(3, 50)
])
print(f"all checks: {str(all_check)}")

print("primes tests passed")
