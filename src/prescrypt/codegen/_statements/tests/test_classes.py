"""Tests for class code generation."""
from __future__ import annotations

from prescrypt import py2js
from prescrypt.testing import js_eval


class TestBasicClasses:
    """Test basic class definition and instantiation."""

    def test_simple_class(self):
        """Test simple class with __init__."""
        code = """
class Foo:
    def __init__(self):
        self.x = 42

f = Foo()
f.x
"""
        js = py2js(code)
        assert js_eval(js) == 42

    def test_class_with_args(self):
        """Test class __init__ with arguments."""
        code = """
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(3, 4)
p.x + p.y
"""
        js = py2js(code)
        assert js_eval(js) == 7

    def test_method_call(self):
        """Test calling instance methods."""
        code = """
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count = self.count + 1
        return self.count

c = Counter()
c.increment()
c.increment()
c.count
"""
        js = py2js(code)
        assert js_eval(js) == 2


class TestInheritance:
    """Test class inheritance."""

    def test_simple_inheritance(self):
        """Test basic inheritance."""
        code = """
class Animal:
    def __init__(self):
        self.alive = True

class Dog(Animal):
    def __init__(self):
        self.alive = True
        self.breed = "mutt"

d = Dog()
d.alive
"""
        js = py2js(code)
        assert js_eval(js) == True

    def test_method_override(self):
        """Test method overriding."""
        code = """
class Base:
    def greet(self):
        return "Hello from Base"

class Sub(Base):
    def greet(self):
        return "Hello from Sub"

s = Sub()
s.greet()
"""
        js = py2js(code)
        assert js_eval(js) == "Hello from Sub"


class TestSuper:
    """Test super() functionality."""

    def test_super_init(self):
        """Test super().__init__() call."""
        code = """
class Base:
    def __init__(self):
        self.base_val = 10

class Sub(Base):
    def __init__(self):
        super().__init__()
        self.sub_val = 20

s = Sub()
s.base_val + s.sub_val
"""
        js = py2js(code)
        assert js_eval(js) == 30

    def test_super_init_with_args(self):
        """Test super().__init__() with arguments."""
        code = """
class Base:
    def __init__(self, x):
        self.x = x

class Sub(Base):
    def __init__(self, x, y):
        super().__init__(x)
        self.y = y

s = Sub(10, 20)
s.x + s.y
"""
        js = py2js(code)
        assert js_eval(js) == 30

    def test_super_method(self):
        """Test super().method() call."""
        code = """
class Base:
    def greet(self):
        return "Hello"

class Sub(Base):
    def greet(self):
        base_greeting = super().greet()
        return base_greeting + " World"

s = Sub()
s.greet()
"""
        js = py2js(code)
        assert js_eval(js) == "Hello World"

    def test_super_attribute(self):
        """Test accessing class attribute via super()."""
        code = """
class Base:
    value = 100

class Sub(Base):
    value = 200

    def get_base_value(self):
        return super().value

s = Sub()
s.get_base_value()
"""
        js = py2js(code)
        assert js_eval(js) == 100

    def test_super_chain(self):
        """Test chaining method calls after super()."""
        code = """
class Base:
    def get_list(self):
        return [1, 2, 3, 2, 1]

class Sub(Base):
    def count_twos(self):
        return super().get_list().count(2)

s = Sub()
s.count_twos()
"""
        js = py2js(code)
        assert js_eval(js) == 2


class TestStaticMethod:
    """Test @staticmethod decorator."""

    def test_staticmethod_basic(self):
        """Test basic static method."""
        code = """
class Math:
    @staticmethod
    def add(a, b):
        return a + b

Math.add(3, 4)
"""
        js = py2js(code)
        assert js_eval(js) == 7

    def test_staticmethod_no_self(self):
        """Test static method doesn't require instance."""
        code = """
class Counter:
    count = 0

    @staticmethod
    def increment():
        return 1

Counter.increment()
"""
        js = py2js(code)
        assert js_eval(js) == 1

    def test_staticmethod_called_on_instance(self):
        """Test static method can be called on instance too."""
        code = """
class Math:
    @staticmethod
    def multiply(a, b):
        return a * b

m = Math()
m.multiply(3, 4)
"""
        js = py2js(code)
        assert js_eval(js) == 12


class TestClassMethod:
    """Test @classmethod decorator."""

    def test_classmethod_basic(self):
        """Test basic class method."""
        code = """
class Counter:
    value = 10

    @classmethod
    def get_value(cls):
        return cls.value

Counter.get_value()
"""
        js = py2js(code)
        assert js_eval(js) == 10

    def test_classmethod_with_args(self):
        """Test class method with additional arguments."""
        code = """
class Factory:
    @classmethod
    def create(cls, x):
        return x * 2

Factory.create(5)
"""
        js = py2js(code)
        assert js_eval(js) == 10

    def test_classmethod_on_instance(self):
        """Test class method can be called on instance."""
        code = """
class Counter:
    value = 100

    @classmethod
    def get_value(cls):
        return cls.value

c = Counter()
c.get_value()
"""
        js = py2js(code)
        assert js_eval(js) == 100


class TestProperty:
    """Test @property decorator."""

    def test_property_getter(self):
        """Test basic property getter."""
        code = """
class Person:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

p = Person("Alice")
p.name
"""
        js = py2js(code)
        assert js_eval(js) == "Alice"

    def test_property_getter_computed(self):
        """Test property getter with computed value."""
        code = """
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    @property
    def area(self):
        return self.width * self.height

r = Rectangle(3, 4)
r.area
"""
        js = py2js(code)
        assert js_eval(js) == 12

    def test_property_setter(self):
        """Test property with setter."""
        code = """
class Counter:
    def __init__(self):
        self._value = 0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v

c = Counter()
c.value = 42
c.value
"""
        js = py2js(code)
        assert js_eval(js) == 42


class TestClassEdgeCases:
    """Additional tests for edge cases and complex scenarios."""

    def test_multiple_inheritance_levels(self):
        """Test inheritance chain of 3 classes."""
        code = """
class A:
    def __init__(self):
        self.a = 1

class B(A):
    def __init__(self):
        super().__init__()
        self.b = 2

class C(B):
    def __init__(self):
        super().__init__()
        self.c = 3

c = C()
c.a + c.b + c.c
"""
        js = py2js(code)
        assert js_eval(js) == 6

    def test_super_with_method_args(self):
        """Test super() method call with arguments."""
        code = """
class Base:
    def add(self, x, y):
        return x + y

class Sub(Base):
    def add(self, x, y):
        result = super().add(x, y)
        return result * 2

s = Sub()
s.add(3, 4)
"""
        js = py2js(code)
        assert js_eval(js) == 14

    def test_class_attribute_and_instance_attribute(self):
        """Test class vs instance attribute precedence."""
        code = """
class Counter:
    count = 0

    def __init__(self):
        self.count = 10

c = Counter()
c.count
"""
        js = py2js(code)
        assert js_eval(js) == 10

    def test_method_returning_self(self):
        """Test method chaining with self return."""
        code = """
class Builder:
    def __init__(self):
        self.value = 0

    def add(self, n):
        self.value = self.value + n
        return self

b = Builder()
b.add(1).add(2).add(3).value
"""
        js = py2js(code)
        assert js_eval(js) == 6

    def test_staticmethod_with_class_reference(self):
        """Test static method that references class attributes."""
        code = """
class Config:
    DEFAULT = 100

    @staticmethod
    def get_default():
        return Config.DEFAULT

Config.get_default()
"""
        js = py2js(code)
        assert js_eval(js) == 100

    def test_classmethod_creating_instance(self):
        """Test class method as factory."""
        code = """
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def origin(cls):
        p = Point(0, 0)
        return p.x + p.y

Point.origin()
"""
        js = py2js(code)
        assert js_eval(js) == 0

    def test_property_with_validation(self):
        """Test property setter with validation logic."""
        code = """
class Temperature:
    def __init__(self):
        self._celsius = 0

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < -273:
            self._celsius = -273
        else:
            self._celsius = value

t = Temperature()
t.celsius = -300
t.celsius
"""
        js = py2js(code)
        assert js_eval(js) == -273

    def test_nested_class_instantiation(self):
        """Test creating class instance inside method."""
        code = """
class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

    def append(self, value):
        self.next = Node(value)
        return self.next.value

n = Node(1)
n.append(2)
"""
        js = py2js(code)
        assert js_eval(js) == 2

    def test_class_with_list_attribute(self):
        """Test class with mutable list attribute."""
        code = """
class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def size(self):
        return len(self.items)

s = Stack()
s.push(1)
s.push(2)
s.push(3)
s.size()
"""
        js = py2js(code)
        assert js_eval(js) == 3

    def test_inheritance_with_overridden_property(self):
        """Test overriding a property in subclass."""
        code = """
class Base:
    @property
    def value(self):
        return 10

class Sub(Base):
    @property
    def value(self):
        return 20

s = Sub()
s.value
"""
        js = py2js(code)
        assert js_eval(js) == 20


class TestSpecialMethods:
    """Test special method dispatch (__len__, __eq__, __getitem__, __setitem__)."""

    def test_len_method(self):
        """Test __len__ is called by len()."""
        code = """
class MyList:
    def __init__(self):
        self.items = [1, 2, 3, 4, 5]

    def __len__(self):
        return len(self.items) * 2

ml = MyList()
len(ml)
"""
        js = py2js(code)
        assert js_eval(js) == 10

    def test_eq_method(self):
        """Test __eq__ is called by == operator."""
        code = """
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

p1 = Point(3, 4)
p2 = Point(3, 4)
p3 = Point(1, 2)
result = []
if p1 == p2:
    result.append(1)
if p1 == p3:
    result.append(2)
len(result)
"""
        js = py2js(code)
        assert js_eval(js) == 1

    def test_getitem_method(self):
        """Test __getitem__ is called by [] operator."""
        code = """
class MyDict:
    def __init__(self):
        self.data = {'a': 1, 'b': 2, 'c': 3}

    def __getitem__(self, key):
        return self.data[key] * 10

md = MyDict()
md['b']
"""
        js = py2js(code)
        assert js_eval(js) == 20

    def test_setitem_method(self):
        """Test __setitem__ is called by []= assignment."""
        code = """
class MyDict:
    def __init__(self):
        self.data = {}
        self.log = []

    def __setitem__(self, key, value):
        self.log.append(key)
        self.data[key] = value * 2

    def __getitem__(self, key):
        return self.data[key]

md = MyDict()
md['x'] = 5
md['y'] = 10
md['x'] + md['y']
"""
        js = py2js(code)
        assert js_eval(js) == 30  # 5*2 + 10*2 = 30

    def test_combined_special_methods(self):
        """Test class with multiple special methods."""
        code = """
class Vector:
    def __init__(self, items):
        self.items = items

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        return self.items[idx]

    def __setitem__(self, idx, value):
        self.items[idx] = value

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for i in range(len(self)):
            if self[i] != other[i]:
                return False
        return True

v1 = Vector([1, 2, 3])
v2 = Vector([1, 2, 3])
v1[0] = 10
result = v1[0] + len(v1)
if v1 == v2:
    result = 0
result
"""
        js = py2js(code)
        assert js_eval(js) == 13  # 10 + 3 = 13, v1 != v2 now

    def test_len_on_regular_objects(self):
        """Test len() still works on lists and strings."""
        code = """
len([1, 2, 3]) + len("hello")
"""
        js = py2js(code)
        assert js_eval(js) == 8

    def test_subscript_on_regular_objects(self):
        """Test subscript still works on lists and dicts."""
        code = """
a = [10, 20, 30]
d = {"x": 100}
a[1] = 25
result = a[0] + a[1] + d["x"]
result
"""
        js = py2js(code)
        assert js_eval(js) == 135  # 10 + 25 + 100
