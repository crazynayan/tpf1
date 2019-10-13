import re
from typing import Tuple, TypeVar, Optional, Union, List

from assembly.directive import Literal
from assembly.file_line import Label, Line
from assembly.instruction_operand import FieldBaseDsp, Bits, FieldIndex, FieldLen
from assembly.macro import SegmentMacro
from config import config
from utils.command import cmd
from utils.data_type import Register
from utils.errors import Error

InstructionType = TypeVar('InstructionType', bound='InstructionGeneric')


class InstructionGeneric:
    def __init__(self):
        self.index: Optional[int] = None
        self.label: Optional[str] = None
        self.command: Optional[str] = None
        self.fall_down: Optional[str] = None
        self.conditions: List = list()

    def __repr__(self) -> str:
        return f"{self.index}:{self.label}:{self.command}"

    def set_operand(self, line: Line, macro: SegmentMacro) -> Tuple[InstructionType, str]:
        return self, Error.NO_ERROR

    @property
    def next_labels(self) -> set:
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

    def get_attribute(self, attribute: str) -> Optional[str]:
        return cmd.check(self.command, attribute)


class FieldBits(InstructionGeneric):
    def __init__(self):
        super().__init__()
        self.field: Optional[FieldBaseDsp] = None
        self.bits: Optional[Bits] = None

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.field},{self.bits}"

    def set_operand(self, line: Line, macro: SegmentMacro) -> Tuple[InstructionType, str]:
        operand1, operand2 = line.split_operands()
        self.field = FieldBaseDsp()
        result = self.field.set(operand1, macro)
        if result == Error.NO_ERROR:
            self.bits = Bits()
            result = self.bits.set(operand2, macro)
        return self, result


class FieldLenField(InstructionGeneric):
    MAX_LEN = 256

    def __init__(self):
        super().__init__()
        self.field_len: Optional[FieldLen] = None
        self.field: Optional[FieldBaseDsp] = None

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.field_len},{self.field}"

    def set_operand(self, line: Line, macro: SegmentMacro) -> Tuple[InstructionType, str]:
        operand1, operand2 = line.split_operands()
        self.field_len = FieldLen()
        operand1 = Literal.update(literal=operand1, macro=macro)
        result = self.field_len.set(operand1, macro, self.MAX_LEN)
        if result == Error.NO_ERROR:
            self.field = FieldBaseDsp()
            operand2 = Literal.update(literal=operand2, macro=macro)
            result = self.field.set(operand2, macro, self.field_len.length)
        return self, result


class FieldLenFieldLen(InstructionGeneric):
    MAX_LEN = 16

    def __init__(self):
        super().__init__()
        self.field_len1: Optional[FieldLen] = None
        self.field_len2: Optional[FieldLen] = None

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.field_len1},{self.field_len2}"

    def set_operand(self, line: Line, macro: SegmentMacro) -> Tuple[InstructionType, str]:
        operand1, operand2 = line.split_operands()
        self.field_len1 = FieldLen()
        operand1 = Literal.update(literal=operand1, macro=macro)
        result = self.field_len1.set(operand1, macro, self.MAX_LEN)
        if result == Error.NO_ERROR:
            self.field_len2 = FieldLen()
            operand2 = Literal.update(literal=operand2, macro=macro)
            result = self.field_len2.set(operand2, macro, self.MAX_LEN)
        return self, result


class FieldLenFieldData(InstructionGeneric):
    MAX_LEN = 16
    MAX_DATA = (1 << 4) - 1

    def __init__(self):
        super().__init__()
        self.field_len: Optional[FieldLen] = None
        self.field: Optional[FieldBaseDsp] = None
        self.data: Optional[int] = None

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.field_len},{self.field},{self.data}"

    def set_operand(self, line: Line, macro: SegmentMacro) -> Tuple[InstructionType, str]:
        operand1, operand2, operand3 = line.split_operands()
        self.field_len = FieldLen()
        result = self.field_len.set(operand1, macro, self.MAX_LEN)
        if result == Error.NO_ERROR:
            self.field = FieldBaseDsp()
            result = self.field.set(operand2, macro)
            if result == Error.NO_ERROR:
                self.data, result = macro.get_value(operand3)
                if result == Error.NO_ERROR and not 0 <= self.data <= 9:
                    result = Error.FLFD_INVALID_DATA
        return self, result


class FieldData(InstructionGeneric):
    DATA_LENGTH = 1     # 1 Byte

    def __init__(self):
        super().__init__()
        self.field: Optional[FieldBaseDsp] = None
        self.data: Optional[int] = None

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.field},{self.data}"

    def set_operand(self, line: Line, macro: SegmentMacro) -> Tuple[InstructionType, str]:
        operand1, operand2 = line.split_operands()
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


class FieldSingle(InstructionGeneric):
    MAX_LEN = 16

    def __init__(self):
        super().__init__()
        self.field: Optional[FieldLen] = None

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.field}"

    def set_operand(self, line: Line, macro: SegmentMacro) -> Tuple[InstructionType, str]:
        self.field = FieldLen()
        result = self.field.set(line.operand, macro, self.MAX_LEN)
        return self, result


class RegisterRegister(InstructionGeneric):
    def __init__(self):
        super().__init__()
        self.reg1: Optional[Register] = None
        self.reg2: Optional[Register] = None

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.reg1},{self.reg2}"

    def set_operand(self, line: Line, macro: SegmentMacro) -> Tuple[InstructionType, str]:
        operand1, operand2 = line.split_operands()
        self.reg1 = Register(operand1)
        self.reg2 = Register(operand2)
        result = Error.NO_ERROR if self.reg1.is_valid() and self.reg2.is_valid() else Error.REG_INVALID
        return self, result


class RegisterFieldIndex(InstructionGeneric):
    def __init__(self):
        super().__init__()
        self.field: Optional[FieldIndex] = None
        self.reg: Optional[Register] = None

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.reg},{self.field}"

    def set_operand(self, line: Line, macro: SegmentMacro) -> Tuple[InstructionType, str]:
        length = int(self.get_attribute('field_len') or 0)
        operand1, operand2 = line.split_operands()
        self.reg = Register(operand1)
        result = Error.NO_ERROR if self.reg.is_valid() else Error.RFX_INVALID_REG
        if result == Error.NO_ERROR:
            self.field = FieldIndex()
            operand2 = Literal.update(literal=operand2, macro=macro)
            result = self.field.set(operand2, macro, length)
        return self, result


class RegisterData(InstructionGeneric):
    DATA_LENGTH = 16    # 16 bits

    def __init__(self):
        super().__init__()
        self.reg: Optional[Register] = None
        self.data: Optional[int] = None

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.reg},{self.data}"

    def set_operand(self, line: Line, macro: SegmentMacro) -> Tuple[InstructionType, str]:
        operand1, operand2 = line.split_operands()
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


class RegisterRegisterField(InstructionGeneric):
    def __init__(self):
        super().__init__()
        self.reg1: Optional[Register] = None
        self.reg2: Optional[Register] = None
        self.field: Optional[FieldBaseDsp] = None

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.reg1},{self.reg2},{self.field}"

    def set_operand(self, line: Line, macro: SegmentMacro) -> Tuple[InstructionType, str]:
        operand1, operand2, operand3 = line.split_operands()
        self.reg1 = Register(operand1)
        self.reg2 = Register(operand2)
        result = Error.NO_ERROR if self.reg1.is_valid() and self.reg2.is_valid() else Error.REG_INVALID
        if result == Error.NO_ERROR:
            self.field = FieldBaseDsp()
            result = self.field.set(operand3, macro, 40)
        return self, result


class RegisterDataField(InstructionGeneric):
    MAX_DATA = (1 << 4) - 1

    def __init__(self):
        super().__init__()
        self.reg: Optional[Register] = None
        self.data: Optional[int] = None
        self.field: Optional[FieldBaseDsp] = None

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.reg},{self.data},{self.field}"

    def set_operand(self, line: Line, macro: SegmentMacro) -> Tuple[InstructionType, str]:
        operand1, operand2, operand3 = line.split_operands()
        self.reg = Register(operand1)
        if self.reg.is_valid():
            self.data, result = macro.get_value(operand2)
            if result == Error.NO_ERROR:
                if isinstance(self.data, int) and 1 <= self.data <= self.MAX_DATA:
                    self.field = FieldBaseDsp()
                    operand3 = Literal.update(literal=operand3, macro=macro)
                    result = self.field.set(operand3, macro, bin(self.data).count('1'))
                else:
                    result = Error.RDF_INVALID_DATA
        else:
            result = Error.REG_INVALID
        return self, result


class Exit(InstructionGeneric):
    pass


class BranchGeneric(InstructionGeneric):
    def __init__(self):
        super().__init__()
        self.branch: Optional[FieldIndex] = None

    def set_branch(self, branch: str, macro: SegmentMacro) -> str:
        self.branch = FieldIndex()
        result = self.branch.set(branch, macro, length=1)
        if result == Error.NO_ERROR:
            if not macro.is_branch(self.branch.name):
                result = Error.BC_INVALID_BRANCH
            elif self.branch.index is not None:
                result = Error.BC_INDEX
        return result

    @property
    def next_labels(self) -> set:
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


class ConditionGeneric(InstructionGeneric):
    def __init__(self):
        super().__init__()
        self.mask: Optional[int] = None

    def set_mask(self, line: Line) -> Tuple[str, str]:
        mask = self.get_attribute('mask')
        result = Error.NO_ERROR
        if mask is not None:
            # This is commands with mnemonics like BP, JNZ, J, B, NOP, BR, BMR
            self.mask = int(mask)
            operand = line.operand
        else:
            # This is commands with mask. BC or JC or BCR
            mask, operand = line.split_operands()
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
    def __init__(self):
        super().__init__()

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.mask},{self.branch}"

    def set_operand(self, line: Line, macro: SegmentMacro) -> Tuple[InstructionType, str]:
        branch, result = self.set_mask(line)
        if result == Error.NO_ERROR:
            result = self.set_branch(branch, macro)
            if self.mask == 0:
                # This is required to ensure that while creating paths, 0 mask branches are ignored
                self.branch = None
        return self, result


class BranchConditionRegister(BranchCondition):
    def __init__(self):
        super().__init__()
        self.reg: Optional[Register] = None

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.mask},{self.reg}"

    def set_operand(self, line: Line, macro: SegmentMacro) -> Tuple[InstructionType, str]:
        reg, result = self.set_mask(line)
        if result == Error.NO_ERROR:
            self.reg = Register(reg)
            if not self.reg.is_valid():
                result = Error.REG_INVALID
        return self, result


class RegisterBranch(BranchGeneric):
    def __init__(self):
        super().__init__()
        self.reg: Optional[Register] = None

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.reg},{self.branch}"

    def set_operand(self, line: Line, macro: SegmentMacro) -> Tuple[InstructionType, str]:
        reg, branch = line.split_operands()
        result = self.set_branch(branch, macro)
        if result == Error.NO_ERROR:
            self.reg = Register(reg)
            if not self.reg.is_valid():
                result = Error.REG_INVALID
        return self, result


class RegisterLabel(InstructionGeneric):
    def __init__(self):
        super().__init__()
        self.reg: Optional[Register] = None
        self.label: Optional[str] = None

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.reg},{self.label}"

    def set_operand(self, line: Line, macro: SegmentMacro) -> Tuple[InstructionType, str]:
        reg, label = line.split_operands()
        self.reg = Register(reg)
        if not self.reg.is_valid():
            result = Error.REG_INVALID
        else:
            if macro.is_branch(label):
                if macro.is_instruction_branch(label):
                    self.label = label
                else:
                    self.label = label + Label.SEPARATOR + '1'
                result = Error.NO_ERROR
            else:
                if label.startswith('*-'):
                    nodes = macro.global_program.segments[macro.seg_name].nodes
                    prior_ins = next(node for _, node in nodes.items() if node.fall_down == line.label)
                    prior_ins_len, _ = macro.get_value(label[2:])
                    if prior_ins.get_attribute('len') == prior_ins_len:
                        self.label = prior_ins.label
                        result = Error.NO_ERROR
                    else:
                        result = Error.RL_INVALID_LEN
                else:
                    result = Error.RL_INVALID_LABEL
        return self, result


class RegisterRegisterBranch(BranchGeneric):
    def __init__(self):
        super().__init__()
        self.reg1: Optional[Register] = None
        self.reg2: Optional[Register] = None

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.reg1},{self.reg2},{self.branch}"

    def set_operand(self, line: Line, macro: SegmentMacro) -> Tuple[InstructionType, str]:
        operand1, operand2, operand3 = line.split_operands()
        result = self.set_branch(operand3, macro)
        if result == Error.NO_ERROR:
            self.reg1 = Register(operand1)
            self.reg2 = Register(operand2)
            if not self.reg1.is_valid() or not self.reg2.is_valid():
                result = Error.REG_INVALID
        return self, result


class SegmentCall(BranchGeneric):
    def __init__(self):
        super().__init__()
        self.seg_name: Optional[str] = None

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.seg_name},{self.branch}"

    def set_operand(self, line: Line, macro: SegmentMacro) -> Tuple[InstructionType, str]:
        self.seg_name = next(iter(line.split_operands()))
        try:
            called_seg = macro.global_program.segments[self.seg_name]
            called_seg.load()
            result = self.set_branch(called_seg.root_label, called_seg.macro)
        except KeyError:
            result = Error.SC_INVALID_SEGMENT
        return self, result


class KeyValue(InstructionGeneric):
    def __init__(self):
        super().__init__()
        self.operands: List[Tuple[str, Union[str, List, None]]] = list()
        self.branches: List[str] = list()

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.operands}"

    def set_operand(self, line: Line, macro: SegmentMacro) -> Tuple[InstructionType, str]:
        operands = line.split_operands()
        for operand in operands:
            key_value = re.split(r"=(?![^()]*[)])", operand)
            if len(key_value) > 1 and key_value[1].startswith('(') and key_value[1].endswith(')'):
                sub_operands = key_value[1][1:-1]
                self.operands.append((key_value[0], list()))
                for sub_operand in sub_operands.split(','):
                    sub_key_value = sub_operand.split('=')
                    value = sub_key_value[1] if len(sub_key_value) > 1 else None
                    self.operands[-1][1].append((sub_key_value[0], value))
                    if macro.is_branch(value):
                        self.branches.append(value)
            else:
                value = key_value[1] if len(key_value) > 1 else None
                self.operands.append((key_value[0], value))
                if macro.is_branch(value):
                    self.branches.append(value)
        return self, Error.NO_ERROR

    def is_key(self, key: str) -> bool:
        return key in self.keys

    def is_sub_key(self, key: str) -> bool:
        return key in self.sub_keys

    def get_value(self, key: str) -> Union[str, List, None]:
        value = next((key_value[1] for key_value in self.operands if key_value[0] == key), None)
        if isinstance(value, list) and all(sub_key_value[1] is None for sub_key_value in value):
            value = [sub_key_value[0] for sub_key_value in value]
        return value

    def get_key_from_value(self, value: Union[str, List]) -> Optional[str]:
        return next((key_value[0] for key_value in self.operands if key_value[1] == value), None)

    @property
    def key_only(self) -> List[str]:
        return [key_value[0] for key_value in self.operands if key_value[1] is None]

    @property
    def keys(self) -> List[str]:
        return [key_value[0] for key_value in self.operands]

    @property
    def sub_keys(self) -> List[str]:
        # Returns all keys that have sub_keys
        return [key_value[0] for key_value in self.operands if isinstance(key_value[1], list)]

    @property
    def sub_key_value(self) -> List[Tuple[str, List]]:
        # Returns all key_value that have sub_keys
        return [key_value for key_value in self.operands if isinstance(key_value[1], list)]

    def get_sub_value(self, key: str, sub_key: str) -> Union[str, FieldBaseDsp]:
        return next((sub_key_value[1] for key_value in self.sub_key_value for sub_key_value in key_value[1]
                     if key_value[0] == key and sub_key_value[0] == sub_key), None)

    def set_sub_value(self, value: FieldBaseDsp, original_value: str, key: str, sub_key: str) -> None:
        key_value_list = self.get_value(key)
        key_value_list.remove((sub_key, original_value))
        key_value_list.append((sub_key, value))

    @property
    def next_labels(self) -> set:
        labels = set(self.branches)
        if self.fall_down:
            labels.add(self.fall_down)
        return labels

    @property
    def goes(self) -> str:
        return next(iter(self.branches), None)


class Dbred(KeyValue):
    def __init__(self):
        super().__init__()

    def set_operand(self, line: Line, macro: SegmentMacro) -> Tuple[InstructionType, str]:
        super().set_operand(line, macro)
        for key_number in range(2, 7):
            key_n = f"KEY{key_number}"
            if not self.is_key(key_n):
                break
            field_name = self.get_sub_value(key_n, 'S')
            if not field_name:
                break
            field = FieldBaseDsp()
            if field.set(field_name, macro) != Error.NO_ERROR:
                raise TypeError
            self.set_sub_value(field, field_name, key_n, 'S')
        return self, Error.NO_ERROR


class Globz(RegisterData):
    def set_operand(self, line: Line, macro: SegmentMacro) -> Tuple[InstructionType, str]:
        globz, result = KeyValue().set_operand(line, macro)
        if result == Error.NO_ERROR:
            if globz.is_key('REGR'):
                base = Register(globz.get_value('REGR'))
            elif globz.is_key('REGS'):
                base = Register(globz.get_value('REGS'))
            else:
                base = None
            if base and base.is_valid():
                macro.load('GLOBAL', base=base.reg)
                self.reg = base
                self.command = 'LHI'
                self.data = config.GLOBAL
            else:
                result = Error.REG_INVALID
        return self, result


class DataMacroDeclaration:
    def __init__(self, line: Line, macro: SegmentMacro):
        data_macro, result = KeyValue().set_operand(line, macro)
        if result != Error.NO_ERROR:
            raise TypeError
        kwargs = dict()
        kwargs['macro_name'] = line.command
        if data_macro.is_key('REG'):
            base = Register(data_macro.get_value('REG'))
            if not base.is_valid():
                raise TypeError
            kwargs['base'] = base.reg
        if data_macro.is_key('SUFFIX'):
            suffix = data_macro.get_value('SUFFIX')
            kwargs['suffix'] = suffix
        macro.load(**kwargs)
