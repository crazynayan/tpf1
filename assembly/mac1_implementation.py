import re
from typing import List, Optional

from assembly.mac0_generic import MacroGeneric
from utils.data_type import DataType
from utils.errors import EquLabelRequiredError, EquDataTypeHasAmpersandError
from utils.file_line import Line


class Dsdc:

    def __init__(self, duplication_factor: int, data_type: str, length: int, start: int,
                 data: Optional[bytearray], expression: List[str]):
        self.duplication_factor: int = duplication_factor
        self.data_type: str = data_type
        self.length: int = length
        self.start: int = start
        self.data: Optional[bytearray] = data
        self.expression: List[str] = expression

    def __repr__(self) -> str:
        return f"{self.duplication_factor}:{self.data_type}:L{self.length}:S{self.start}" \
               f":{self.data}:{len(self.expression)}"


class DataMacroImplementation(MacroGeneric):

    def __init__(self, name):
        super().__init__(name)
        self._command['DS'] = self.ds
        self._command['EQU'] = self.equ
        self._command['ORG'] = self.org
        self._command['DSECT'] = self.dsect

    def _dsdc(self, operand: str, literal: bool = False) -> Dsdc:
        # (^\d+)?(?:[(]([^)]+)[)])?([CXHFDBZPAY]D?)(?:L([\d]+))?(?:L[(]([^)]+)[)])?(?:[']([^']+)['])?(?:[(]([^)]+)[)])?
        operands = next(iter(re.findall(
            r"(^\d+)?"  # 0 Duplication Factor - A number. (Optional)
            r"(?:[(]([^)]+)[)])?"  # 1 Duplication Factor - Expression enclosed in paranthesis (Optional)
            r"([CXHFDBZPAY]D?)"  # 2 Data Type - Valid Single character Data type. (Note: FD is valid)
            r"(?:L([\d]+))?"  # 3 Length - L followed by a number. (Optional)
            r"(?:L[(]([^)]+)[)])?"  # 4 Length - L followed by a expression enclosed in paranthesis. (Optional)
            r"(?:[']([^']+)['])?"  # 5 Data - Enclosed in quotes. (Optional)
            r"(?:[(]([^)]+)[)])?",  # 6 Data - Enclosed in parenthesis. (Optional)
            operand)))
        # Duplication Factor
        duplication_factor = int(operands[0]) if operands[0] else 1
        if operands[1]:
            duplication_factor = self.get_value(operands[1])
        # Data Type
        data_type = operands[2]
        # Align to boundary
        align_to_boundary = 0
        boundary = DataType(data_type).align_to_boundary
        if boundary > 0 and self._location_counter % boundary > 0:
            align_to_boundary = boundary - self._location_counter % boundary
        # Length
        if operands[3]:
            length = int(operands[3])
            align_to_boundary = 0
        elif operands[4]:
            length = self.get_value(operands[4])
            align_to_boundary = 0
        else:
            length = None
        # Data
        number_of_data_operands = 1
        data = list()
        expression = list()
        if operands[5]:
            data_type_object = DataType(data_type, input=operands[5])
            length = length or data_type_object.length
            data = data_type_object.to_bytes(length)
        elif operands[6]:
            expression = operands[6].split(',')
            number_of_data_operands = len(expression)
            length = length or DataType(data_type).default_length
            # Only for literal generate address constants. For DC, they will be generated separately.
            if literal:
                data = bytearray()
                for operand in expression:
                    data.extend(DataType(data_type, input=str(self.get_value(operand))).to_bytes(length))
        else:
            length = length or DataType(data_type).default_length
        # Start (after boundary alignment) and End (After duplication factor)
        start = self._location_counter + align_to_boundary
        self._location_counter = start + duplication_factor * length * number_of_data_operands
        if self._location_counter > self._max_counter:
            self._max_counter = self._location_counter
        dsdc = Dsdc(duplication_factor, data_type, length, start, data, expression)
        return dsdc

    def ds(self, line: Line) -> List[Dsdc]:
        operands = line.split_operands()
        dsdc: Dsdc = self._dsdc(operands[0])
        dsdc_list: List[Dsdc] = [dsdc]
        if line.label:
            self.add_label(line.label, dsdc.start, dsdc.length, self.name)
        if len(operands) > 1:
            for operand in operands[1:]:
                dsdc_list.append(self._dsdc(operand))  # Increment location counter for multiple values
        return dsdc_list

    def equ(self, line: Line) -> None:
        if line.label is None:
            raise EquLabelRequiredError
        operands = line.split_operands()
        dsp_operand = operands[0]
        length = 1
        if dsp_operand == '*':
            dsp = self._location_counter
        elif not set("+-*/").intersection(dsp_operand):
            if dsp_operand.isdigit():
                dsp = int(dsp_operand)
            elif re.match(r"^[CXHFDBZPAY]'[^']+'$", dsp_operand) is not None:
                if '&' in dsp_operand:
                    raise EquDataTypeHasAmpersandError
                dsp = DataType(dsp_operand[0], input=dsp_operand[2:-1]).value
            else:
                if dsp_operand[0] == '&':
                    raise EquDataTypeHasAmpersandError
                field = self.lookup(dsp_operand)
                dsp = field.dsp
                length = field.length
        else:
            dsp = self.get_value(dsp_operand)
        if len(operands) > 1:
            length = self.get_value(operands[1])
        self.add_label(line.label, dsp, length, self.name)
        return

    def org(self, line: Line) -> None:
        if line.operand is None:
            self._location_counter = self._max_counter
        else:
            self._location_counter = self.get_value(line.operand)
        return

    def dsect(self, line: Line) -> None:
        self._location_counter = 0
        self._max_counter = 0
        self.add_label(line.label, 0, 0, line.label)
        return
