"""Test @dataclass decorator."""
from __future__ import annotations

from dataclasses import dataclass


# Basic dataclass
@dataclass
class Point:
    x: int
    y: int


p1 = Point(3, 4)
print(p1.x)
print(p1.y)
print(repr(p1))


# Dataclass with default values
@dataclass
class Config:
    debug: bool = False
    timeout: int = 30
    name: str = "default"


c1 = Config()
print(c1.debug)
print(c1.timeout)
print(c1.name)

c2 = Config(True, 60, "custom")
print(c2.debug)
print(c2.timeout)
print(c2.name)


# Mixed defaults (fields without defaults must come first)
@dataclass
class Person:
    name: str
    age: int
    city: str = "Unknown"


person = Person("Alice", 30)
print(person.name)
print(person.age)
print(person.city)
print(repr(person))


# Equality testing
@dataclass
class Coordinate:
    x: int
    y: int


coord1 = Coordinate(1, 2)
coord2 = Coordinate(1, 2)
coord3 = Coordinate(3, 4)

print(coord1 == coord2)  # True - same values
print(coord1 == coord3)  # False - different values


# Dataclass with eq=False
@dataclass(eq=False)
class UniqueItem:
    value: int


item1 = UniqueItem(42)
item2 = UniqueItem(42)
print(item1 == item2)  # False - no __eq__, different instances


# Dataclass with additional methods
@dataclass
class Rectangle:
    width: int
    height: int

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)


rect = Rectangle(5, 3)
print(rect.area())
print(rect.perimeter())
print(repr(rect))


# Dataclass with classmethod
@dataclass
class Vector:
    x: float
    y: float

    @classmethod
    def zero(cls):
        return cls(0, 0)

    @classmethod
    def unit_x(cls):
        return cls(1, 0)

    def magnitude(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5


v0 = Vector.zero()
print(v0.x)
print(v0.y)

v1 = Vector.unit_x()
print(int(v1.magnitude()))

v2 = Vector(3, 4)
print(int(v2.magnitude()))


# Dataclass with staticmethod
@dataclass
class Counter:
    value: int = 0

    @staticmethod
    def is_positive(n):
        return n > 0


counter = Counter(5)
print(Counter.is_positive(counter.value))
print(Counter.is_positive(-1))


# Nested dataclasses
@dataclass
class Address:
    street: str
    city: str


@dataclass
class Employee:
    name: str
    address: Address


addr = Address("123 Main St", "Springfield")
emp = Employee("Bob", addr)
print(emp.name)
print(emp.address.street)
print(emp.address.city)


# Repr with string fields (should be quoted)
@dataclass
class Book:
    title: str
    author: str
    year: int


book = Book("1984", "George Orwell", 1949)
print(repr(book))


print("dataclasses tests done")
