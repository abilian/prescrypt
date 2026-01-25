"""Test match statements (structural pattern matching)."""
from __future__ import annotations


# Basic literal matching
def describe_number(n):
    match n:
        case 0:
            return "zero"
        case 1:
            return "one"
        case 2:
            return "two"
        case _:
            return "many"

print(describe_number(0))
print(describe_number(1))
print(describe_number(2))
print(describe_number(99))


# Match with multiple patterns (OR)
def is_weekend(day):
    match day:
        case "Saturday" | "Sunday":
            return True
        case _:
            return False

print(is_weekend("Saturday"))
print(is_weekend("Monday"))


# Match with capture
def process(value):
    match value:
        case 0:
            return "zero"
        case n:
            return f"got {n}"

print(process(0))
print(process(42))


# Match with guard
def classify(n):
    match n:
        case x if x < 0:
            return "negative"
        case x if x == 0:
            return "zero"
        case x if x > 0:
            return "positive"

print(classify(-5))
print(classify(0))
print(classify(10))


# Match on type/structure (list patterns)
def handle_list(lst):
    match lst:
        case []:
            return "empty"
        case [x]:
            return f"single: {x}"
        case [x, y]:
            return f"pair: {x}, {y}"
        case [x, y, *rest]:
            return f"first two: {x}, {y}, rest: {rest}"

print(handle_list([]))
print(handle_list([1]))
print(handle_list([1, 2]))
print(handle_list([1, 2, 3, 4, 5]))


# Match with nested patterns
def analyze_point(point):
    match point:
        case (0, 0):
            return "origin"
        case (0, y):
            return f"on y-axis at {y}"
        case (x, 0):
            return f"on x-axis at {x}"
        case (x, y):
            return f"point at ({x}, {y})"

print(analyze_point((0, 0)))
print(analyze_point((0, 5)))
print(analyze_point((3, 0)))
print(analyze_point((3, 4)))


# Match with dict patterns
def handle_command(cmd):
    match cmd:
        case {"action": "quit"}:
            return "quitting"
        case {"action": "move", "x": x, "y": y}:
            return f"moving to ({x}, {y})"
        case {"action": action}:
            return f"unknown action: {action}"
        case _:
            return "invalid command"

print(handle_command({"action": "quit"}))
print(handle_command({"action": "move", "x": 10, "y": 20}))
print(handle_command({"action": "jump"}))
print(handle_command("invalid"))


# String matching
def parse_color(color):
    match color:
        case "red":
            return (255, 0, 0)
        case "green":
            return (0, 255, 0)
        case "blue":
            return (0, 0, 255)
        case _:
            return (0, 0, 0)

print(parse_color("red"))
print(parse_color("green"))
print(parse_color("unknown"))


# Singleton patterns (None, True, False)
def check_value(v):
    match v:
        case None:
            return "nothing"
        case True:
            return "yes"
        case False:
            return "no"
        case _:
            return "something else"

print(check_value(None))
print(check_value(True))
print(check_value(False))
print(check_value(42))


# Class patterns
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def describe_point(p):
    match p:
        case Point(x=0, y=0):
            return "origin"
        case Point(x=0, y=y):
            return f"on y-axis at {y}"
        case Point(x=x, y=0):
            return f"on x-axis at {x}"
        case Point(x=x, y=y):
            return f"point at ({x}, {y})"
        case _:
            return "not a point"

print(describe_point(Point(0, 0)))
print(describe_point(Point(0, 5)))
print(describe_point(Point(3, 0)))
print(describe_point(Point(3, 4)))


# Star patterns at different positions
def first_and_last(items):
    match items:
        case []:
            return "empty"
        case [only]:
            return f"single: {only}"
        case [first, *_, last]:
            return f"first={first}, last={last}"

print(first_and_last([]))
print(first_and_last([1]))
print(first_and_last([1, 2]))
print(first_and_last([1, 2, 3, 4, 5]))


def get_tail(items):
    match items:
        case [*rest, last]:
            return [rest, last]
        case _:
            return None

print(get_tail([1, 2, 3]))


# Nested sequence patterns
def process_nested(data):
    match data:
        case [[a, b], c]:
            return a + b + c
        case [x, [y, z]]:
            return x * (y + z)
        case _:
            return 0

print(process_nested([[1, 2], 3]))
print(process_nested([2, [3, 4]]))


# Guard with sequence pattern
def sum_if_positive(lst):
    match lst:
        case [a, b] if a > 0 and b > 0:
            return a + b
        case [a, b]:
            return 0
        case _:
            return -1

print(sum_if_positive([3, 4]))
print(sum_if_positive([-1, 5]))
print(sum_if_positive([1]))


print("match tests done")
