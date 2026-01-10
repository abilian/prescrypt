# nested exceptions
from __future__ import annotations


def f():
    try:
        foo()
    except:
        print("except 1")
        try:
            baz()
        except:
            print("except 2")
        bar()

try:
    f()
except:
    print("f except")
