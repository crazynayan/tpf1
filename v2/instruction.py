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

    def get_next(self):
        return list() if self.fall_down is None else [self.fall_down]

    @staticmethod
    def split_operands(operands):
        # Split operands separated by commas. Ignore commas enclosed in parenthesis.
        return re.split(r",(?![^()]*\))", operands)


class FieldBits(Instruction):
    def __init__(self, label, command):
        super().__init__(label, command)
        self.field = None
        self.bits = None

    @classmethod
    def from_operand(cls, label, command, operand, macro):
        instruction = cls(label, command)
        operand1, operand2 = instruction.split_operands(operand)
        field, result = FieldBaseDsp.from_operand(operand1, macro)
        if result != Error.NO_ERROR:
            return instruction, result
        bits, result = Bits.from_operand(operand2, macro)
        if result != Error.NO_ERROR:
            return instruction, result
        instruction.field = field
        instruction.bits = bits
        return instruction, Error.NO_ERROR
