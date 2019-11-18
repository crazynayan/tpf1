import re
from typing import Optional, Dict, Tuple, List

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
    def is_literal(self) -> bool:
        return self.dsp > 0xFFF

    def set_branch(self) -> None:
        self._branch = 1

    def to_dict(self) -> dict:
        self_dict = self.__dict__.copy()
        del self_dict['_branch']
        return self_dict


class MacroGeneric:

    def __init__(self, name):
        self.name = name
        self._symbol_table: Dict[str, LabelReference] = dict()
        self._index: Dict[str, List[Tuple[str, int]]] = dict()
        self._command: Dict[str, callable] = dict()
        self._location_counter: int = 0
        self._max_counter: int = 0

    @property
    def all_labels(self) -> Dict[str, LabelReference]:
        return self._symbol_table

    @property
    def indexed_data(self) -> Dict[str, List[Tuple[str, int]]]:
        return self._index

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

    def add_label(self, label: str, dsp: int, length: int, name: str) -> LabelReference:
        label_ref = LabelReference(label, dsp, length, name)
        self._symbol_table[label] = label_ref
        index_label = name + str(dsp)
        if index_label not in self._index:
            self._index[index_label] = list()
        self._index[index_label].append((label, length))
        return label_ref
