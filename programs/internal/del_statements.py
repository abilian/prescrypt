"""Test del statements - basic cases that work with transpiler."""
from __future__ import annotations


# Note: del for list/dict subscripts is not yet fully supported
# This test documents the expected behavior for future implementation

# Delete variable (local scope)
def test_del_var():
    x = 10
    y = x
    del x
    return y


print(test_del_var())  # 10


# Delete from dict using pop (workaround for del d[key])
d = {"a": 1, "b": 2, "c": 3}
d.pop("b")
print("a" in d)  # True
print("b" in d)  # False
print(d["a"])  # 1


# Delete from list using pop (workaround for del lst[idx])
lst = [1, 2, 3, 4, 5]
lst.pop(2)  # Remove item at index 2
print(lst)  # [1, 2, 4, 5]

lst2 = [10, 20, 30]
lst2.pop()  # Remove last item
print(lst2)  # [10, 20]


# Remove by value
lst3 = [1, 2, 3, 2, 4]
lst3.remove(2)  # Removes first 2
print(lst3)  # [1, 3, 2, 4]


print("del_statements tests done")
