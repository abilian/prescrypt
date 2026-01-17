"""Test higher-order functions (decorator patterns).

Note: Prescrypt does not support @decorator syntax. This test demonstrates
higher-order function patterns that work without decorator syntax.
"""
from __future__ import annotations


# Higher-order function that wraps another function
def make_doubler(func):
    def wrapper(x):
        return func(x) * 2
    return wrapper


def square(x):
    return x * x

doubled_square = make_doubler(square)
print(doubled_square(3))  # (3*3) * 2 = 18


# Function returning function (currying)
def make_adder(n):
    def add(x):
        return x + n
    return add

add_five = make_adder(5)
print(add_five(10))  # 15


# Function composition
def compose(f, g):
    def combined(x):
        return f(g(x))
    return combined


def inc(x):
    return x + 1


def double(x):
    return x * 2

inc_then_double = compose(double, inc)
print(inc_then_double(5))  # (5 + 1) * 2 = 12


# Closure with state
def make_counter():
    count = [0]
    def counter():
        count[0] += 1
        return count[0]
    return counter

c = make_counter()
print(c())  # 1
print(c())  # 2
print(c())  # 3


# Simple class
class Counter:
    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1
        return self.value


obj = Counter()
print(obj.increment())  # 1
print(obj.increment())  # 2
