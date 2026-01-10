# test nested whiles within a try-except
from __future__ import annotations

while 1:
    print(1)
    try:
        print(2)
        while 1:
            print(3)
            break
    except:
        print(4)
    print(5)
    break
