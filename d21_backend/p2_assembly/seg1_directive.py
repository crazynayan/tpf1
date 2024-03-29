from copy import deepcopy
from typing import List, Optional

from d21_backend.p1_utils.data_type import Register
from d21_backend.p1_utils.errors import UsingInvalidError, DropInvalidError
from d21_backend.p1_utils.file_line import Line
from d21_backend.p2_assembly.mac1_implementation import Dc
from d21_backend.p2_assembly.mac2_data_macro import get_macros
from d21_backend.p2_assembly.seg0_generic import SegmentGeneric


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
        self._command['DATAS'] = self.datas

    def dc(self, line: Line) -> None:
        dc_list: List[Dc] = super().ds(line)
        dc_list[0].label = line.label if line.label else str()
        self.dc_list.extend(dc_list)
        return

    def ds(self, line: Line) -> None:
        super().ds(line)
        if line.label and self.name == self.seg_name:
            self.lookup(line.label).set_branch()
        return

    def ds_dc_lst(self, line: Line) -> int:
        operands = line.split_operands()
        if line.label:
            self._location_counter = self.evaluate(line.label)
        ds_dc: Dc = self._get_dc(operands[0])
        if line.command == "DC":
            ds_dc.label = line.label if line.label else str()
            self.dc_list.append(ds_dc)
            if len(operands) > 1:
                for operand in operands[1:]:
                    self.dc_list.append(self._get_dc(operand))
        return ds_dc.length

    def equ_lst(self, line: Line) -> int:
        operands = line.split_operands()
        if len(operands) > 1 and operands[1]:
            length = self.get_value(operands[1])
        else:
            length = 1
        return length

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
        if not self._counters:
            self._location_counter, self._max_counter = 0, 0
            return
        self._location_counter, self._max_counter = self._counters
        self._counters = None

    def begin(self, _) -> None:
        self._location_counter = 8

    def push(self, _) -> None:
        self._using_stack.append(deepcopy(self._using))

    def pop(self, _) -> None:
        self._using = self._using_stack.pop()

    def drop(self, line: Line) -> None:
        operands = line.split_operands()
        registers = [Register(operand) for operand in operands]
        if any(not register.is_valid() for register in registers):
            raise DropInvalidError(line)
        for drop_register in registers:
            self._using[drop_register.value] = list()

    def using(self, line: Line) -> None:
        operands = line.split_operands()
        dsect_name = self.name if operands[0] == '*' else operands[0]
        for index in range(1, len(operands)):
            self.set_using(dsect_name, base_reg=operands[index])

    def datas(self, line: Line) -> None:
        operands = line.split_operands()
        if len(operands) < 3:
            raise UsingInvalidError(line)
        suffix: Optional[str] = operands[1] if operands[1] else None
        try:
            for operand in operands[2:]:
                if operand not in get_macros():
                    raise UsingInvalidError(line)
                self.load_macro(operand, base=operands[0], suffix=suffix)
        except UsingInvalidError:
            raise UsingInvalidError(line)
        return

    def no_operation(self, _) -> None:
        return
