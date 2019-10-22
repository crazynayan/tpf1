from typing import Optional, List, Set, TypeVar

from assembly2.seg2_ins_operand import FieldBaseDsp, Bits, FieldIndex, FieldLen
from utils.command import cmd
from utils.data_type import Register
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

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.field},{self.bits}"


class FieldLenField(InstructionGeneric):
    MAX_LEN = 256

    def __init__(self, line: Line, field_len: FieldLen, field: FieldBaseDsp):
        super().__init__(line)
        self.field_len: FieldLen = field_len
        self.field: FieldBaseDsp = field

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.field_len},{self.field}"


class FieldLenFieldLen(InstructionGeneric):
    MAX_LEN = 16

    def __init__(self, line: Line, field_len1: FieldLen, field_len2: FieldLen):
        super().__init__(line)
        self.field_len1: FieldLen = field_len1
        self.field_len2: FieldLen = field_len2

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.field_len1},{self.field_len2}"


class FieldData(InstructionGeneric):
    MAX_VALUE = 255

    def __init__(self, line: Line, field: FieldBaseDsp, data: int):
        super().__init__(line)
        self.field: FieldBaseDsp = field
        self.data: int = data

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.field},{self.data}"


class FieldSingle(InstructionGeneric):
    MAX_LEN = 16

    def __init__(self, line: Line, field: FieldBaseDsp):
        super().__init__(line)
        self.field: FieldBaseDsp = field

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.field}"


class FieldLenFieldData(InstructionGeneric):
    MAX_LEN = 16
    MAX_VALUE = 9

    def __init__(self, line: Line, field_len: FieldLen, field: FieldBaseDsp, data: int):
        super().__init__(line)
        self.field_len: FieldLen = field_len
        self.field: FieldBaseDsp = field
        self.data: int = data

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.field_len},{self.field},{self.data}"


class RegisterRegister(InstructionGeneric):

    def __init__(self, line: Line, reg1: Register, reg2: Register):
        super().__init__(line)
        self.reg1: Register = reg1
        self.reg2: Register = reg2

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.reg1},{self.reg2}"


class RegisterFieldIndex(InstructionGeneric):

    def __init__(self, line: Line, reg: Register, field: FieldIndex):
        super().__init__(line)
        self.reg: Register = reg
        self.field: FieldIndex = field

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.reg},{self.field}"


class RegisterData(InstructionGeneric):
    DATA_LENGTH = 16  # 16 bits

    def __init__(self, line: Line, reg: Register, data: int):
        super().__init__(line)
        self.reg: Register = reg
        self.data: int = data

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.reg},{self.data}"


class RegisterRegisterField(InstructionGeneric):

    def __init__(self, line: Line, reg1: Register, reg2: Register, field: FieldBaseDsp):
        super().__init__(line)
        self.reg1: Register = reg1
        self.reg2: Register = reg2
        self.field: FieldBaseDsp = field

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.reg1},{self.reg2},{self.field}"


class RegisterDataField(InstructionGeneric):
    MAX_VALUE = 15  # 4 bits can only store from 0 to 15

    def __init__(self, line: Line, reg: Register, data: int, field: FieldBaseDsp):
        super().__init__(line)
        self.reg: Register = reg
        self.data: int = data
        self.field: FieldBaseDsp = field

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.reg},{self.data},{self.field}"


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

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.mask},{self.branch}"


class BranchConditionRegister(BranchCondition):
    def __init__(self, line: Line, mask: int, reg: Register):
        super().__init__(line, None, mask)
        self.reg: Register = reg

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.mask},{self.reg}"


class RegisterBranch(BranchGeneric):
    def __init__(self, line: Line, reg: Register, branch: FieldIndex):
        super().__init__(line, branch)
        self.reg: Register = reg

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.reg},{self.branch}"


class RegisterRegisterBranch(BranchGeneric):
    def __init__(self, line: Line, reg1: Register, reg2: Register, branch: FieldIndex):
        super().__init__(line, branch)
        self.reg1: Register = reg1
        self.reg2: Register = reg2

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.reg1},{self.reg2},{self.branch}"


class RegisterLabel(InstructionGeneric):
    def __init__(self, line: Line, reg: Register, label: str):
        super().__init__(line)
        self.reg: Register = reg
        self.ex_label: str = label

    def __repr__(self) -> str:
        return f"{super().__repr__()}:{self.reg},{self.ex_label}"
