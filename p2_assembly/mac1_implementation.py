from typing import List, Optional

from p1_utils.data_type import DataType
from p1_utils.errors import EquLabelRequiredError, EquDataTypeHasAmpersandError, DcInvalidError, \
    NotFoundInSymbolTableError
from p1_utils.file_line import Line
from p2_assembly.mac0_generic import MacroGeneric


class Dc:

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

    @staticmethod
    def get_parameter_in_parenthesis(operand: str) -> str:
        if len(operand) < 3 or operand[0] != '(':
            return str()
        parenthesis = 0
        end = 0
        for index, char in enumerate(operand):
            if char == '(':
                parenthesis += 1
            if char == ')':
                parenthesis -= 1
            if parenthesis == 0:
                end = index + 1
                break
        if not end:
            return str()
        return operand[: end]

    @staticmethod
    def get_digits(operand: str) -> str:
        index = 0
        for char in operand[index:]:
            if not char.isdigit():
                break
            index += 1
        return operand[:index]

    def _get_dc(self, operand: str, literal: bool = False) -> Dc:
        index = 0
        # Duplication Factor
        duplication_factor = 1
        duplication_factor_text = self.get_digits(operand)
        if duplication_factor_text:
            duplication_factor = int(duplication_factor_text)
            index = len(duplication_factor_text)
        elif operand[0] == '(':
            duplication_factor_text = self.get_parameter_in_parenthesis(operand)
            if not duplication_factor_text:
                raise DcInvalidError
            duplication_factor = self.get_value(duplication_factor_text[1:-1])
            index = len(duplication_factor_text)
        # Data Type
        data_type = operand[index]
        if data_type not in 'CXHFDBZPAY':
            raise DcInvalidError
        index += 1
        if data_type == 'F' and len(operand) > index and operand[index] == 'D':
            data_type = 'FD'
            index += 1
        # Align to boundary
        align_to_boundary = 0
        boundary = DataType(data_type).align_to_boundary
        if boundary > 0 and self._location_counter % boundary > 0:
            align_to_boundary = boundary - self._location_counter % boundary
        # Length
        length = None
        if len(operand) > index and operand[index] == 'L':
            align_to_boundary = 0
            index += 1
            length_text = self.get_digits(operand[index:])
            if length_text:
                length = int(length_text)
            elif operand[index] == '(':
                length_text = self.get_parameter_in_parenthesis(operand[index:])
                length = self.get_value(length_text[1:-1])
            else:
                raise DcInvalidError
            index += len(length_text)
        # Data
        number_of_data_operands = 1
        data = list()
        expression = list()
        if len(operand) > index:
            if operand[index] == "'":
                if operand[-1] != "'":
                    raise DcInvalidError
                data_type_object = DataType(data_type, input=operand[index + 1: -1])
                length = length or data_type_object.length
                data = data_type_object.to_bytes(length)
            elif operand[index] == '(':
                data_text = self.get_parameter_in_parenthesis(operand[index:])
                expression = data_text[1:-1].split(',')
                if len(expression) == 0 or not expression[0]:
                    raise DcInvalidError
                number_of_data_operands = len(expression)
                length = length or DataType(data_type).default_length
                # Only for literal generate address constants. For DC, they will be generated separately.
                if literal:
                    data = bytearray()
                    for operand in expression:
                        data.extend(DataType(data_type, input=str(self.get_value(operand))).to_bytes(length))
            else:
                raise DcInvalidError
        else:
            length = length or DataType(data_type).default_length
        # Start (after boundary alignment) and End (After duplication factor)
        start = self._location_counter + align_to_boundary
        self._location_counter = start + duplication_factor * length * number_of_data_operands
        if self._location_counter > self._max_counter:
            self._max_counter = self._location_counter
        dc = Dc(duplication_factor, data_type, length, start, data, expression)
        return dc

    def ds(self, line: Line) -> List[Dc]:
        operands = line.split_operands()
        try:
            ds: Dc = self._get_dc(operands[0])
        except DcInvalidError:
            raise DcInvalidError(line)
        dc_list: List[Dc] = [ds]
        if line.label:
            self.add_label(line.label, ds.start, ds.length, self.name)
        if len(operands) > 1:
            for operand in operands[1:]:
                dc_list.append(self._get_dc(operand))  # Increment location counter for multiple values
        return dc_list

    def equ(self, line: Line) -> None:
        if line.label is None:
            raise EquLabelRequiredError(line)
        operands = line.split_operands()
        dsp_operand = operands[0]
        length = 1
        if dsp_operand[0] == '&' or (len(dsp_operand) > 1 and dsp_operand[1] == "'" and dsp_operand[0] != 'L'
                                     and '&' in dsp_operand):
            raise EquDataTypeHasAmpersandError(line)
        if len(operands) > 1:
            length = self.get_value(operands[1])
        try:
            self.add_label(line.label, self.get_value(dsp_operand), length, self.name, self.is_based(dsp_operand))
        except NotFoundInSymbolTableError:
            raise NotFoundInSymbolTableError(line)
        return

    def org(self, line: Line) -> None:
        self._location_counter = self.get_value(line.operand) if line.operand else self._max_counter
        return

    def dsect(self, line: Line) -> None:
        self._location_counter = 0
        self._max_counter = 0
        self.add_label(line.label, 0, 0, line.label)
        return
