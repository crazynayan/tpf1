from typing import Optional, List, Set, TypeVar, Tuple

from assembly2.seg2_operand import InstructionOperand, FieldBaseDsp, Bits, FieldIndex, FieldLen
from utils.command import cmd
from utils.data_type import Register
from utils.errors import RegisterInvalidError, ConditionMaskError, FieldDataInvalidError
from utils.file_line import Line

InstructionType = TypeVar('InstructionType', bound='InstructionGeneric')


class InstructionGeneric:

    def __init__(self, line: Line):
        self.index: int = line.index
        self.label: Optional[str] = line.label
        self.command: str = line.command
        self.fall_down: Optional[str] = None
        self.conditions: List[InstructionType] = list()

    def __repr__(self) -> str:
        return f"{self.index}:{self.label}:{self.command}"

    @property
    def next_labels(self) -> Set[str]:
        labels = {condition.branch.name for condition in self.conditions if condition.is_check_cc and condition.branch}
        if self.fall_down:
            labels.add(self.fall_down)
        return labels

    @property
    def goes(self) -> str:
        return next((condition.goes for condition in self.conditions if condition.goes), None)

    @property
    def on(self) -> str:
        return next((condition.command for condition in self.conditions if condition.is_check_cc), None)

    @property
    def is_fall_down(self) -> bool:
        return True if not self.get_attribute('no_fall_down') else False

    @property
    def is_check_cc(self) -> bool:
        return True if self.get_attribute('check_cc') else False

    def get_attribute(self, cmd_attribute: str) -> Optional[str]:
        return cmd.check(self.command, cmd_attribute)


class FieldBits(InstructionGeneric):

    def __init__(self, line: Line, field: FieldBaseDsp, bits: Bits):
        super().__init__(line)
        self.field: FieldBaseDsp = field
        self.bits: Bits = bits


class RegisterRegister(InstructionGeneric):

    def __init__(self, line: Line, reg1: Register, reg2: Register):
        super().__init__(line)
        self.reg1: Register = reg1
        self.reg2: Register = reg2


class RegisterFieldIndex(InstructionGeneric):

    def __init__(self, line: Line, reg: Register, field: FieldIndex):
        super().__init__(line)
        self.reg: Register = reg
        self.field: FieldIndex = field


class FieldLenField(InstructionGeneric):
    MAX_LEN = 256

    def __init__(self, line: Line, field_len: FieldLen, field: FieldBaseDsp):
        super().__init__(line)
        self.field_len: FieldLen = field_len
        self.field: FieldBaseDsp = field


class FieldLenFieldLen(InstructionGeneric):
    MAX_LEN = 16

    def __init__(self, line: Line, field_len1: FieldLen, field_len2: FieldLen):
        super().__init__(line)
        self.field_len1: FieldLen = field_len1
        self.field_len2: FieldLen = field_len2


class FieldData(InstructionGeneric):
    MAX_VALUE = 255

    def __init__(self, line: Line, field: FieldBaseDsp, data: int):
        super().__init__(line)
        self.field: FieldBaseDsp = field
        self.data: int = data


class BranchGeneric(InstructionGeneric):

    def __init__(self, line: Line, branch: Optional[FieldIndex]):
        super().__init__(line)
        self.branch: Optional[FieldIndex] = branch

    @property
    def next_labels(self) -> Set[str]:
        labels = set()
        if self.fall_down:
            labels.add(self.fall_down)
        if self.branch:
            labels.add(self.branch.name)
        return labels

    @property
    def goes(self) -> str:
        return self.branch.name if self.branch is not None else None

    @property
    def on(self) -> str:
        return self.command


class BranchCondition(BranchGeneric):

    def __init__(self, line: Line, branch: Optional[FieldIndex], mask: int):
        super().__init__(line, branch)
        self.mask: int = mask


class InstructionImplementation(InstructionOperand):

    def __init__(self, name: str):
        super().__init__(name)
        self._command['OI'] = self.field_bits
        self._command['NI'] = self.field_bits
        self._command['XI'] = self.field_bits
        self._command['TM'] = self.field_bits
        self._command['CLC'] = self.field_len_field
        self._command['MVC'] = self.field_len_field
        self._command['XC'] = self.field_len_field
        self._command['OC'] = self.field_len_field
        self._command['NC'] = self.field_len_field
        self._command['PACK'] = self.field_len_field_len
        self._command['UNPK'] = self.field_len_field_len
        self._command['CLI'] = self.field_data
        self._command['MVI'] = self.field_data
        self._command['LTR'] = self.reg_reg
        self._command['LR'] = self.reg_reg
        self._command['AR'] = self.reg_reg
        self._command['SR'] = self.reg_reg
        self._command['BCTR'] = self.reg_reg
        self._command['L'] = self.reg_field_index
        self._command['LA'] = self.reg_field_index
        self._command['IC'] = self.reg_field_index
        self._command['STH'] = self.reg_field_index
        self._command['N'] = self.reg_field_index
        self._command['ST'] = self.reg_field_index
        self._command['STC'] = self.reg_field_index
        self._command['CVB'] = self.reg_field_index
        self._command['CVD'] = self.reg_field_index
        self._command['CH'] = self.reg_field_index
        self._command['BC'] = self.branch_condition
        self._command['B'] = self.branch_condition
        self._command['NOP'] = self.branch_condition
        self._command['BZ'] = self.branch_condition
        self._command['BNZ'] = self.branch_condition
        self._command['BO'] = self.branch_condition
        self._command['BNO'] = self.branch_condition
        self._command['BE'] = self.branch_condition
        self._command['BNE'] = self.branch_condition
        self._command['BM'] = self.branch_condition
        self._command['BNM'] = self.branch_condition
        self._command['BP'] = self.branch_condition
        self._command['BNP'] = self.branch_condition
        self._command['BH'] = self.branch_condition
        self._command['BNH'] = self.branch_condition
        self._command['BL'] = self.branch_condition
        self._command['BNL'] = self.branch_condition
        self._command['JC'] = self.branch_condition
        self._command['J'] = self.branch_condition
        self._command['JNOP'] = self.branch_condition
        self._command['JZ'] = self.branch_condition
        self._command['JNZ'] = self.branch_condition
        self._command['JO'] = self.branch_condition
        self._command['JNO'] = self.branch_condition
        self._command['JE'] = self.branch_condition
        self._command['JNE'] = self.branch_condition
        self._command['JM'] = self.branch_condition
        self._command['JNM'] = self.branch_condition
        self._command['JP'] = self.branch_condition
        self._command['JNP'] = self.branch_condition
        self._command['JH'] = self.branch_condition
        self._command['JNH'] = self.branch_condition
        self._command['JL'] = self.branch_condition
        self._command['JNL'] = self.branch_condition
        self._command['ENTNC'] = self.instruction_generic
        self._command['BACKC'] = self.instruction_generic
        self._command['EXITC'] = self.instruction_generic

    @staticmethod
    def instruction_generic(line: Line) -> InstructionGeneric:
        return InstructionGeneric(line)

    def equ(self, line: Line) -> InstructionGeneric:
        if not self.check(line.label):
            super().equ(line)
        return InstructionGeneric(line)

    def ds(self, line: Line) -> InstructionGeneric:
        if not self.check(line.label):
            super().ds(line)
        return InstructionGeneric(line)

    def field_bits(self, line: Line) -> FieldBits:
        operand1, operand2 = line.split_operands()
        field = self.field_base_dsp(operand1)
        bits = self.get_bits(operand2)
        return FieldBits(line, field, bits)

    def field_len_field(self, line: Line) -> FieldLenField:
        operand1, operand2 = line.split_operands()
        field_len = self.field_len(operand1, FieldLenField.MAX_LEN)
        field = self.field_base_dsp(operand2)
        return FieldLenField(line, field_len, field)

    def field_len_field_len(self, line: Line) -> FieldLenFieldLen:
        operand1, operand2 = line.split_operands()
        field_len1 = self.field_len(operand1, FieldLenFieldLen.MAX_LEN)
        field_len2 = self.field_len(operand2, FieldLenFieldLen.MAX_LEN)
        return FieldLenFieldLen(line, field_len1, field_len2)

    def field_data(self, line: Line) -> FieldData:
        operand1, operand2 = line.split_operands()
        field = self.field_base_dsp(operand1)
        data = self.get_value(operand2)
        if not 0 <= data <= FieldData.MAX_VALUE:
            raise FieldDataInvalidError
        return FieldData(line, field, data)

    @staticmethod
    def reg_reg(line: Line) -> RegisterRegister:
        operand1, operand2 = line.split_operands()
        reg1 = Register(operand1)
        reg2 = Register(operand2)
        if not reg1.is_valid() or not reg2.is_valid():
            raise RegisterInvalidError
        return RegisterRegister(line, reg1, reg2)

    def reg_field_index(self, line: Line) -> RegisterFieldIndex:
        operand1, operand2 = line.split_operands()
        reg = Register(operand1)
        if not reg.is_valid():
            raise RegisterInvalidError
        field = self.field_index(operand2)
        return RegisterFieldIndex(line, reg, field)

    @staticmethod
    def _get_mask(line: Line) -> Tuple[int, str, str]:
        mask = cmd.check(line.command, 'mask')
        command = line.command
        if mask is not None:
            # This is commands with mnemonics like BP, JNZ, J, B, NOP, BR, BMR
            mask = int(mask)
            operand = line.operand
        else:
            # This is commands with mask. BC or JC or BCR
            mask, operand = line.split_operands()
            mask = int(mask)
            commands = cmd.get_commands('mask', mask)
            mnemonic = next((command for command in commands
                             if cmd.check(line.command, 'len') == cmd.check(command, 'len')), None)
            if mnemonic is None:
                raise ConditionMaskError
            command = mnemonic
        return mask, operand, command

    def branch_condition(self, line: Line) -> BranchCondition:
        mask, operand, command = self._get_mask(line)
        line.command = command
        if mask == 0:
            branch = None
        else:
            branch = self.get_branch(operand)
        return BranchCondition(line, branch, mask)
