import pytest

from .utils import check


@pytest.mark.skip(reason="Needs list comprehension and other codegen fixes")
def test_primes():
    expr = f"all([eratosthene(n) == gries_misra(n)[0] for n in range(3, 100)])"
    check("primes", expr, True)
