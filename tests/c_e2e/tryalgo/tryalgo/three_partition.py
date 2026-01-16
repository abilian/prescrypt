#!/usr/bin/env python3
"""\
subsetsum

jill-jênn vie et christoph dürr - 2015-2019
"""


# snip{


def three_partition(x: list[int]) -> tuple[int, int, int] | None:
    """partition a set of integers in 3 parts of same total value

    :param x: table of nonnegative values
    :returns: triplet of the integers encoding the sets, or None otherwise
    :complexity: :math:`O(2^{2n})`
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
# snip}
