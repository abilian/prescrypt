class A:
    def __init__(self):
        self.a = 1

    def f(self, b):
        return self.a + b


# FIXME: not working
# print(A().f(1))
