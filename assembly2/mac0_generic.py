import re
from typing import Optional, Dict

from utils.data_type import DataType
from utils.errors import NotFoundInSymbolTableError


class LabelReference:

    def __init__(self, label=None, dsp=None, length=None, name=None):
        self.label: Optional[str] = label
        self.dsp: Optional[int] = dsp
        self.length: Optional[int] = length
        self.name: Optional[str] = name  # Macro name or Segment name or Dsect name
        self._branch: int = 0  # Code cannot branch to this label.

    def __repr__(self):
        return f'{self.label}:{self.dsp}:{self.length}:{self.name}'

    @property
    def is_branch(self) -> bool:
        return self._branch > 0

    @property
    def is_instruction_branch(self) -> bool:
        return self._branch == 2

    @property
    def is_literal(self) -> bool:
        return self.dsp > 0xFFF

    def set_branch(self) -> None:
        self._branch = 1

    def set_instruction_branch(self) -> None:
        self._branch = 2


class Dsdc:

    def __init__(self, duplication_factor: int, data_type: str, length: int, start: int,
                 data: Optional[bytearray] = None):
        self.duplication_factor: int = duplication_factor
        self.data_type: str = data_type
        self.length: int = length
        self.start: int = start
        self.data: Optional[bytearray] = data


class MacroGeneric:

    def __init__(self, name):
        self.name = name
        self._symbol_table: Dict[str, LabelReference] = dict()
        self._command: Dict[str, callable] = dict()
        self._location_counter: int = 0
        self._max_counter: int = 0

    @property
    def all_labels(self) -> Dict[str, LabelReference]:
        return self._symbol_table

    def check(self, label: str) -> bool:
        return label in self._symbol_table

    def lookup(self, label: str) -> LabelReference:
        field = next(iter(label.split('&')))
        try:
            return self._symbol_table[field]
        except KeyError:
            raise NotFoundInSymbolTableError

    def evaluate(self, expression: str) -> int:
        if expression.isdigit():
            return int(expression)
        if expression.startswith("L'"):
            value = self.lookup(expression[2:]).length
        else:
            value = self.lookup(expression).dsp
        return value

    def get_value(self, operand: str) -> int:
        if operand.isdigit():
            return int(operand)
        data_list = re.findall(r"[CXHFDBZPAY]D?'[^']+'", operand)
        value_list = list()
        if data_list:
            operand = re.sub(r"[CXHFDBZPAY]D?'[^']+'", '~', operand)
            for data in data_list:
                value = DataType(data[0], input=data[2:-1]).value
                value_list.insert(0, value)
        exp_list = re.split(r"([+*()-])", operand)
        if len(exp_list) == 1 and data_list:
            return value_list.pop()
        exp_list = [expression for expression in exp_list if expression and expression not in '()']
        eval_list = list()
        for index, expression in enumerate(exp_list):
            if expression == '+' or expression == '-' or (expression == '*' and index % 2 == 1):
                eval_list.append(expression)
            else:
                if expression == '~':
                    value = value_list.pop()
                elif expression == '*':
                    value = self._location_counter
                else:
                    value = self.evaluate(expression)
                eval_list.append(str(value))
        return eval(''.join(eval_list))

    def _dsdc(self, operand: str) -> Dsdc:
        # (^\d*)([CXHFDBZPAY]D?)(?:L([\d]+))?(?:L[(]([^)]+)[)])?(?:[']([^']+)['])?(?:[(]([^)]+)[)])?
        operands = next(iter(re.findall(
            r"(^\d*)"  # 0 Duplication Factor - A number. (Optional)
            r"([CXHFDBZPAY]D?)"  # 1 Data Type - Valid Single character Data type. (Note: FD is valid)
            r"(?:L([\d]+))?"  # 2 Length - L followed by a number. (Optional)
            r"(?:L[(]([^)]*)[)])?"  # 3 Length - L followed by a expression enclosed in paranthesis. (Optional)
            r"(?:[']([^']*)['])?"  # 4 Data - Enclosed in quotes. (Optional)
            r"(?:[(]([^)]*)[)])?",  # 5 Data - Enclosed in parenthesis. (Optional)
            operand)))
        # Duplication Factor
        duplication_factor = int(operands[0]) if operands[0] else 1
        # Data Type
        data_type = operands[1]
        # Align to boundary
        align_to_boundary = 0
        boundary = DataType(data_type).align_to_boundary
        if boundary > 0 and self._location_counter % boundary > 0:
            align_to_boundary = boundary - self._location_counter % boundary
        # Length
        if operands[2]:
            length = int(operands[2])
            align_to_boundary = 0
        elif operands[3]:
            length = self.get_value(operands[3])
            align_to_boundary = 0
        else:
            length = None
        # Data
        if operands[4]:
            data_type_object = DataType(data_type, input=operands[4])
            length = length or data_type_object.length
            data = data_type_object.to_bytes(length)
        elif operands[5]:
            data = bytearray()
            for operand in operands[5].split(','):
                number = self.get_value(operand)
                data_type_object = DataType(data_type, input=str(number))
                length = length or data_type_object.default_length
                data.extend(data_type_object.to_bytes(length))
        else:
            data = None
            length = length or DataType(data_type).default_length
        # Start (after boundary alignment) and End (After duplication factor)
        start = self._location_counter + align_to_boundary
        self._location_counter = start + duplication_factor * length
        if self._location_counter > self._max_counter:
            self._max_counter = self._location_counter
        dsdc = Dsdc(duplication_factor, data_type, length, start, data)
        return dsdc
