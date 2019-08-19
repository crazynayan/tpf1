import re

from v2.data_type import FieldBaseDsp, Bits, FieldIndex, FieldLen, Register
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
        labels = {condition.branch.name for condition in self.conditions if condition.is_check_cc and condition.branch}
        if self.fall_down:
            labels.add(self.fall_down)
        return labels

    @property
    def goes(self):
        return next((condition.goes for condition in self.conditions if condition.goes), None)

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


class BranchGeneric(Instruction):
    def __init__(self, label, command):
        super().__init__(label, command)
        self.branch = None

    def set_branch(self, branch, macro):
        self.branch = FieldIndex()
        result = self.branch.set(branch, macro, length=1)
        if result == Error.NO_ERROR:
            if self.branch.name not in macro.data_map:
                result = Error.BC_INVALID_BRANCH
            elif self.branch.index is not None:
                result = Error.BC_INDEX
        return result

    @property
    def next_labels(self):
        labels = set()
        if self.fall_down:
            labels.add(self.fall_down)
        if self.branch:
            labels.add(self.branch.name)
        return labels

    @property
    def goes(self):
        return self.branch.name if self.branch is not None else None

    @property
    def on(self):
        return self.command


class ConditionGeneric(Instruction):
    def __init__(self, label, command):
        super().__init__(label, command)
        self.mask = None

    def set_mask(self, operand):
        mask = self.get_attribute('mask')
        result = Error.NO_ERROR
        if mask is not None:
            # This is commands with mnemonics like BP, JNZ, J, B, NOP, BR, BMR
            self.mask = int(mask)
        else:
            # This is commands with mask. BC or JC or BCR
            mask, operand = self.split_operands(operand)
            self.mask = int(mask)
            commands = cmd.get_commands('mask', self.mask)
            command = next((command for command in commands
                            if cmd.check(self.command, 'len') == cmd.check(command, 'len')), None)
            if command is None:
                result = Error.BC_INVALID_MASK
            else:
                self.command = command
        return operand, result


class BranchCondition(BranchGeneric, ConditionGeneric):
    def __init__(self, label, command):
        super().__init__(label, command)

    def set_operand(self, operand, macro):
        branch, result = self.set_mask(operand)
        if result == Error.NO_ERROR:
            result = self.set_branch(branch, macro)
            if self.mask == 0:
                # This is required to ensure that while creating paths, 0 mask branches are ignored
                self.branch = None
        return self, result


class BranchConditionRegister(BranchCondition):
    def __init__(self, label, command):
        super().__init__(label, command)
        self.reg = None

    def set_operand(self, operand, macro):
        reg, result = self.set_mask(operand)
        if result == Error.NO_ERROR:
            self.reg = Register(reg)
            if not self.reg.is_valid():
                result = Error.REG_INVALID
        return self, result


class BranchSave(BranchGeneric):
    def __init__(self, label, command):
        super().__init__(label, command)
        self.reg = None

    def set_operand(self, operand, macro):
        operand1, operand2 = self.split_operands(operand)
        result = self.set_branch(operand2, macro)
        if result == Error.NO_ERROR:
            self.reg = Register(operand1)
            if not self.reg.is_valid():
                result = Error.REG_INVALID
        return self, result
