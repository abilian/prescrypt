"""Test builtin functions."""
from __future__ import annotations


# any() and all()
print(any([False, False, True]))  # True
print(any([False, False, False]))  # False
print(any([]))  # False

print(all([True, True, True]))  # True
print(all([True, False, True]))  # False
print(all([]))  # True


# filter()
nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = list(filter(lambda x: x % 2 == 0, nums))
print(evens)  # [2, 4, 6, 8, 10]


# map()
squares = list(map(lambda x: x * x, [1, 2, 3, 4, 5]))
print(squares)  # [1, 4, 9, 16, 25]


# zip()
names = ["Alice", "Bob", "Charlie"]
ages = [25, 30, 35]
pairs = list(zip(names, ages))
print(len(pairs))  # 3
print(pairs[0][0])  # Alice
print(pairs[0][1])  # 25


# enumerate()
items = ["x", "y", "z"]
for i, item in enumerate(items):
    print(i, item)


# reversed()
forward = [1, 2, 3, 4, 5]
backward = list(reversed(forward))
print(backward)  # [5, 4, 3, 2, 1]


# iter() and next()
it = iter([10, 20, 30])
print(next(it))  # 10
print(next(it))  # 20
print(next(it))  # 30


# round()
print(round(3.7))  # 4
print(round(3.2))  # 3
print(round(3.14159, 2))  # 3.14


# divmod()
result = divmod(17, 5)
print(result[0])  # 3
print(result[1])  # 2


# pow()
print(pow(2, 10))  # 1024
print(pow(3, 3))  # 27


# isinstance()
print(isinstance(42, int))  # True
print(isinstance("hello", str))  # True
print(isinstance([1, 2], list))  # True


# getattr/setattr/hasattr
class Obj:
    x = 10


obj = Obj()
print(getattr(obj, "x"))  # 10
print(getattr(obj, "y", "default"))  # default
print(hasattr(obj, "x"))  # True
print(hasattr(obj, "y"))  # False

setattr(obj, "y", 20)
print(obj.y)  # 20


# abs
print(abs(-5))  # 5
print(abs(5))  # 5


# min/max
print(min(3, 1, 4, 1, 5))  # 1
print(max(3, 1, 4, 1, 5))  # 5
print(min([3, 1, 4]))  # 1
print(max([3, 1, 4]))  # 4


# sum
print(sum([1, 2, 3, 4, 5]))  # 15
print(sum([1, 2, 3], 10))  # 16 (with start value)


# sorted
print(sorted([3, 1, 4, 1, 5]))  # [1, 1, 3, 4, 5]
print(sorted([3, 1, 4], reverse=True))  # [4, 3, 1]


print("builtin_functions tests done")
