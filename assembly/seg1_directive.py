from typing import List

from assembly.mac1_implementation import Dsdc
from assembly.seg0_generic import SegmentGeneric
from utils.data_type import Register
from utils.errors import UsingInvalidError, DropInvalidError
from utils.file_line import Line


class DirectiveImplementation(SegmentGeneric):

    def __init__(self, name):
        super().__init__(name)
        self._command['DC'] = self.dc
        self._command['CSECT'] = self.csect
        self._command['PGMID'] = self.begin
        self._command['BEGIN'] = self.begin
        self._command['PUSH'] = self.push
        self._command['POP'] = self.pop
        self._command['DROP'] = self.drop
        self._command['USING'] = self.using
        self._command['LTORG'] = self.no_operation
        self._command['FINIS'] = self.no_operation
        self._command['END'] = self.no_operation
        self._command['EJECT'] = self.no_operation
        self._command['PRINT'] = self.no_operation
        self._command['SPACE'] = self.no_operation

    def dc(self, line: Line) -> None:
        dc_list: List[Dsdc] = super().ds(line)
        self.dc_list.extend(dc_list)
        return

    def ds(self, line: Line) -> None:
        super().ds(line)
        if line.label and self.name == self.seg_name:
            self.lookup(line.label).set_branch()
        return

    def equ(self, line: Line) -> None:
        super().equ(line)
        if self.lookup(line.label).dsp == self._location_counter and self.name == self.seg_name:
            self.lookup(line.label).set_branch()
        return

    def dsect(self, line: Line) -> None:
        if self.name == self.seg_name and self._counters is None:
            self._counters = self._location_counter, self._max_counter
        self.name = line.label
        super().dsect(line)

    def csect(self, _) -> None:
        self.name = self.seg_name
        self._location_counter, self._max_counter = self._counters
        self._counters = None

    def begin(self, _) -> None:
        self._location_counter = 8

    def push(self, _) -> None:
        self._using_stack.append(self._using.copy())

    def pop(self, _) -> None:
        self._using = self._using_stack.pop()

    def drop(self, line: Line) -> None:
        operands = line.split_operands()
        if len(operands) != 1 or not Register(operands[0]).is_valid():
            raise DropInvalidError
        self._using = {macro_name: register for macro_name, register in self._using.items()
                       if register.reg != Register(operands[0]).reg}

    def using(self, line: Line) -> None:
        operands = line.split_operands()
        if len(operands) != 2:
            raise UsingInvalidError
        base = Register(operands[1])
        if not base.is_valid():
            raise UsingInvalidError
        dsect_name = self.name if operands[0] == '*' else operands[0]
        self.set_using(dsect_name, base)

    def no_operation(self, _) -> None:
        return
