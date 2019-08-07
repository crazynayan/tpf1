import re

from v2.data_type import FieldBaseDsp, Bits, Register, FieldIndex, FieldLen
from v2.errors import Error
from v2.command import cmd


class Instruction:
    def __init__(self, label, command):
        self.label = label
        self.command = command
        self.fall_down = None
        self.conditions = list()

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
        labels = {condition.branch for condition in self.conditions if condition.is_check_cc and condition.branch}
        if self.fall_down:
            labels.add(self.fall_down)
        return labels

    @property
    def goes(self):
        return next((condition.branch for condition in self.conditions if condition.is_check_cc), None)

    @property
    def on(self):
        return next((condition.command for condition in self.conditions if condition.is_check_cc), None)

    @property
    def is_fall_down(self):
        return True if not self.get_attribute('no_fall_down') else False

    @property
    def is_check_cc(self):
        return True if self.get_attribute('check_cc') else False

    @staticmethod
    def split_operands(operands):
        # Split operands separated by commas. Ignore commas enclosed in parenthesis.
        return re.split(r",(?![^()]*\))", operands)

    def get_attribute(self, attribute):
        return cmd.check(self.command, attribute)


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
    DATA_LENGTH = 1     # 1 Byte

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


class RegisterData(Instruction):
    DATA_LENGTH = 16    # 16 bits

    def __init__(self, label, command):
        super().__init__(label, command)
        self.reg = None
        self.data = None

    def set_operand(self, operand, macro):
        operand1, operand2 = self.split_operands(operand)
        self.reg = Register(operand1)
        if self.reg.is_valid():
            self.data, result = macro.get_value(operand2)
            if result == Error.NO_ERROR:
                if self.data >= 1 << self.DATA_LENGTH:
                    result = Error.RD_INVALID_NUMBER
                elif self.data < -1 << self.DATA_LENGTH - 1:
                    result = Error.RD_INVALID_NUMBER
                elif self.data >= 1 << self.DATA_LENGTH - 1:
                    self.data -= 1 << self.DATA_LENGTH
        else:
            result = Error.REG_INVALID
        return self, result


class RegisterRegisterField(Instruction):
    def __init__(self, label, command):
        super().__init__(label, command)
        self.reg1 = None
        self.reg2 = None
        self.field = None

    def set_operand(self, operand, macro):
        operand1, operand2, operand3 = self.split_operands(operand)
        self.reg1 = Register(operand1)
        self.reg2 = Register(operand2)
        result = Error.NO_ERROR if self.reg1.is_valid() and self.reg2.is_valid() else Error.REG_INVALID
        if result == Error.NO_ERROR:
            self.field = FieldBaseDsp()
            result = self.field.set(operand3, macro, 40)
        return self, result


class RegisterDataField(Instruction):
    MAX_DATA = (1 << 4) - 1

    def __init__(self, label, command):
        super().__init__(label, command)
        self.reg = None
        self.data = None
        self.field = None

    def set_operand(self, operand, macro):
        operand1, operand2, operand3 = self.split_operands(operand)
        self.reg = Register(operand1)
        if self.reg.is_valid():
            self.data, result = macro.get_value(operand2)
            if result == Error.NO_ERROR:
                if isinstance(self.data, int) and 1 <= self.data <= self.MAX_DATA:
                    self.field = FieldBaseDsp()
                    result = self.field.set(operand3, macro, bin(self.data).count('1'))
                else:
                    result = Error.RDF_INVALID_DATA
        else:
            result = Error.REG_INVALID
        return self, result


class Exit(Instruction):
    pass


class BranchCondition(Instruction):

    def __init__(self, label, command):
        super().__init__(label, command)
        self.mask = 0
        self.branch = None
        self.index = None

    @staticmethod
    def split_label(operand):
        label_reg = re.split(r"[()]", operand)
        if len(label_reg) == 1:
            return label_reg[0], None
        else:
            return label_reg[0], label_reg[1]

    def set_operand(self, operand, macro):
        mask = self.get_attribute('mask')
        if mask is not None:
            # This is commands with mnemonics like BP, JNZ, J, B, NOP
            self.mask = int(mask)
            self.branch, self.index = self.split_label(operand)
            result = Error.NO_ERROR if self.index is None else Error.BC_INDEX
            if self.mask == 0:
                self.branch = None
        else:
            # This is commands with mask. BC or JC
            operand1, operand2 = self.split_operands(operand)
            self.branch, self.index = self.split_label(operand2)
            self.mask = int(operand1)
            result = Error.NO_ERROR if self.index is None else Error.BC_INDEX
            if self.mask == 0:
                self.branch = None
            if result == Error.NO_ERROR:
                command = next(iter(cmd.get_commands('mask', self.mask)), None)
                if command is None:
                    result = Error.BC_INVALID_MASK
                else:
                    self.command = command
        return self, result

    @property
    def next_labels(self):
        labels = set()
        if self.fall_down:
            labels.add(self.fall_down)
        if self.branch:
            labels.add(self.branch)
        return labels

    @property
    def goes(self):
        return self.branch

    @property
    def on(self):
        return self.command
