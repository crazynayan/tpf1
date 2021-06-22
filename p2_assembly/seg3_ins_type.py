from typing import Optional, Set, TypeVar

from p1_utils.data_type import Register
from p1_utils.file_line import Line
from p2_assembly.seg2_ins_operand import FieldBaseDsp, Bits, FieldIndex, FieldLen


class InstructionGeneric:

    def __init__(self, line: Line):
        self.index: int = line.index
        self.label: Optional[str] = line.label
        self.command: str = line.command
        self.fall_down: Optional[str] = None

    def __repr__(self) -> str:
        return f"{self.index:04}:{self.label}:{self.command}"

    @property
    def next_labels(self) -> Set[str]:
        labels = set()
        if self.fall_down:
            labels.add(self.fall_down)
        return labels

    @property
    def goes(self) -> Optional[str]:
        return None

    @property
    def on(self) -> str:
        return self.command


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

    def __init__(self, line: Line, field: FieldLen):
        super().__init__(line)
        self.field: FieldLen = field

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
    DATA_LENGTH = 16  # 32 bits

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
    MAX_VALUE = 15

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
        return f"{InstructionGeneric.__repr__(self)}:{self.mask},{self.reg}"


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


InstructionType = TypeVar("InstructionType", bound=InstructionGeneric)
