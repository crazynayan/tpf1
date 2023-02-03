from typing import Optional


class A:

    def __init__(self, number):
        self.name = f"A{number}"
        self.b: Optional[B] = None

    def __repr__(self):
        return self.name


class B:
    def __init__(self, number: int):
        self.name = f"B{number}"
        self.a: Optional[A] = None

    def __repr__(self):
        return self.name
