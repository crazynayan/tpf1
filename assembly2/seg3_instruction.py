from typing import Optional, List, Set, TypeVar

from assembly.file_line import Line
from assembly2.seg2_operand import InstructionOperand, FieldBaseDsp, Bits
from utils.command import cmd

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


class InstructionImplementation(InstructionOperand):

    def __init__(self, name: str):
        super().__init__(name)
        self._command['OI'] = self.field_bits
        self._command['NI'] = self.field_bits
        self._command['XI'] = self.field_bits
        self._command['TM'] = self.instruction_generic
        self._command['BZ'] = self.instruction_generic
        self._command['ENTNC'] = self.instruction_generic

    @staticmethod
    def instruction_generic(line: Line) -> InstructionGeneric:
        return InstructionGeneric(line)

    def equ(self, line: Line) -> InstructionGeneric:
        super().equ(line)
        return InstructionGeneric(line)

    def ds(self, line: Line) -> InstructionGeneric:
        super().ds(line)
        return InstructionGeneric(line)

    def field_bits(self, line: Line) -> FieldBits:
        operand1, operand2 = line.split_operands()
        field = self.field_base_dsp(operand1)
        bits = self.get_bits(operand2)
        return FieldBits(line, field, bits)
