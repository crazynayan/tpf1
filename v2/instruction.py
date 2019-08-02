import re

from v2.data_type import FieldBaseDsp, Bits, Register, FieldIndex, FieldLen
from v2.errors import Error
from v2.command import cmd


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

    @classmethod
    def from_operand(cls, label, command, operand, macro):
        instruction = cls(label, command)
        return instruction.set_operand(operand, macro)

    def set_operand(self, operand, macro):
        return self, Error.NO_ERROR

    @property
    def next_labels(self):
        return set() if self.fall_down is None else {self.fall_down}

    @staticmethod
    def split_operands(operands):
        # Split operands separated by commas. Ignore commas enclosed in parenthesis.
        return re.split(r",(?![^()]*\))", operands)

    def get_attribute(self, attribute):
        return cmd.check(self.command, attribute)


class Conditional(Instruction):
    def __init__(self, label, command, goes, on):
        Instruction.__init__(self, label, command)
        self.goes = goes
        self.on = on
        self.before_goes = 0

    def __repr__(self):
        return f"{super().__repr__()}:on {self.on}:goes to {self.goes}"

    @classmethod
    def from_operand_condition(cls, label, command, operand, macro, goes, on):
        instruction = cls(label, command, goes, on)
        return instruction.set_operand(operand, macro)

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

    def set_operand(self, operand, macro):
        operand1, operand2 = self.split_operands(operand)
        self.field = FieldBaseDsp()
        result = self.field.set(operand1, macro)
        if result == Error.NO_ERROR:
            self.bits = Bits()
            result = self.bits.set(operand2, macro)
        return self, result


class FieldBitsConditional(FieldBits, Conditional):
    def __init__(self, label, command, goes, on):
        Conditional.__init__(self, label, command, goes, on)


class FieldLenField(Instruction):
    MAX_LEN = 256

    def __init__(self, label, command):
        Instruction.__init__(self, label, command)
        self.field_len = None
        self.field = None

    def set_operand(self, operand, macro):
        operand1, operand2 = self.split_operands(operand)
        self.field_len = FieldLen()
        result = self.field_len.set(operand1, macro, self.MAX_LEN)
        if result == Error.NO_ERROR:
            self.field = FieldBaseDsp()
            result = self.field.set(operand2, macro, self.field_len.length)
        return self, result


class FieldLenFieldConditional(FieldLenField, Conditional):
    def __init__(self, label, command, goes, on):
        Conditional.__init__(self, label, command, goes, on)


class FieldLenFieldLen(Instruction):
    MAX_LEN = 16

    def __init__(self, label, command):
        Instruction.__init__(self, label, command)
        self.field_len1 = None
        self.field_len2 = None

    def set_operand(self, operand, macro):
        operand1, operand2 = self.split_operands(operand)
        self.field_len1 = FieldLen()
        result = self.field_len1.set(operand1, macro, self.MAX_LEN)
        if result == Error.NO_ERROR:
            self.field_len2 = FieldLen()
            result = self.field_len2.set(operand2, macro, self.MAX_LEN)
        return self, result


class FieldData(Instruction):
    DATA_LENGTH = 1

    def __init__(self, label, command):
        Instruction.__init__(self, label, command)
        self.field = None
        self.data = None

    def set_operand(self, operand, macro):
        operand1, operand2 = self.split_operands(operand)
        self.field = FieldBaseDsp()
        result = self.field.set(operand1, macro)
        if result == Error.NO_ERROR:
            self.data, result = macro.get_value(operand2)
            if result == Error.NO_ERROR:
                if isinstance(self.data, int) and not 0 <= self.data <= (1 << 8 * self.DATA_LENGTH) - 1:
                    result = Error.FD_INVALID_DATA
                elif isinstance(self.data, str) and len(self.data) > self.DATA_LENGTH:
                    result = Error.FD_INVALID_DATA
        return self, result


class FieldDataConditional(FieldData, Conditional):
    def __init__(self, label, command, goes, on):
        Conditional.__init__(self, label, command, goes, on)


class RegisterRegister(Instruction):
    def __init__(self, label, command):
        Instruction.__init__(self, label, command)
        self.reg1 = None
        self.reg2 = None

    def set_operand(self, operand, macro):
        operand1, operand2 = self.split_operands(operand)
        self.reg1 = Register(operand1)
        self.reg2 = Register(operand2)
        result = Error.NO_ERROR if self.reg1.is_valid() and self.reg2.is_valid() else Error.REG_INVALID
        return self, result


class RegisterRegisterConditional(RegisterRegister, Conditional):
    def __init__(self, label, command, goes, on):
        Conditional.__init__(self, label, command, goes, on)


class RegisterFieldIndex(Instruction):
    def __init__(self, label, command):
        Instruction.__init__(self, label, command)
        self.field = None
        self.reg = None

    def set_operand(self, operand, macro):
        length = int(self.get_attribute('field_len'))
        operand1, operand2 = self.split_operands(operand)
        self.reg = Register(operand1)
        result = Error.NO_ERROR if self.reg.is_valid() else Error.RFX_INVALID_REG
        if result == Error.NO_ERROR:
            self.field = FieldIndex()
            result = self.field.set(operand2, macro, length)
        return self, result


class RegisterFieldIndexConditional(RegisterFieldIndex, Conditional):
    def __init__(self, label, command, goes, on):
        Conditional.__init__(self, label, command, goes, on)
