import re

from v2.data_type import FieldBaseDsp, Bits
from v2.errors import Error


class Instruction:
    def __init__(self, label, command):
        self.label = label
        self.command = command
        self.fall_down = None

    def __repr__(self):
        if self.fall_down is None:
            return f"{self.label}:{self.command}"
        else:
            return f"{self.label}:{self.command}:falls to {self.fall_down}"

    @property
    def next_labels(self):
        return set() if self.fall_down is None else {self.fall_down}

    @staticmethod
    def split_operands(operands):
        # Split operands separated by commas. Ignore commas enclosed in parenthesis.
        return re.split(r",(?![^()]*\))", operands)


class Conditional(Instruction):
    def __init__(self, label, command, goes, on):
        Instruction.__init__(self, label, command)
        self.goes = goes
        self.on = on

    def __repr__(self):
        return f"{super().__repr__()}:on {self.on}:goes to {self.goes}"

    @property
    def next_labels(self):
        references = {self.goes}
        if self.fall_down is not None:
            references.add(self.fall_down)
        return references


class FieldBits(Instruction):
    def __init__(self, label, command):
        Instruction.__init__(self, label, command)
        self.field = None
        self.bits = None

    @classmethod
    def from_operand(cls, label, command, operand, macro):
        instruction = cls(label, command)
        return instruction.set_operand(operand, macro)

    def set_operand(self, operand, macro):
        operand1, operand2 = self.split_operands(operand)
        field, result = FieldBaseDsp.from_operand(operand1, macro)
        if result != Error.NO_ERROR:
            return self, result
        bits, result = Bits.from_operand(operand2, macro)
        if result != Error.NO_ERROR:
            return self, result
        self.field = field
        self.bits = bits
        return self, Error.NO_ERROR


class FieldBitsConditional(FieldBits, Conditional):
    def __init__(self, label, command, goes, on):
        Conditional.__init__(self, label, command, goes, on)

    @classmethod
    def from_operand_condition(cls, label, command, operand, macro, goes, on):
        instruction = cls(label, command, goes, on)
        return instruction.set_operand(operand, macro)
