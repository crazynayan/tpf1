import re
from typing import Optional, Dict, Tuple, List

from p1_utils.data_type import DataType, Register
from p1_utils.errors import NotFoundInSymbolTableError


class LabelReference:

    def __init__(self, label=None, dsp=None, length=None, name=None, based=True):
        self.label: Optional[str] = label
        self.dsp: Optional[int] = dsp
        self.length: Optional[int] = length
        self.name: Optional[str] = name  # Macro name or Segment name or Dsect name
        self._branch: int = 0  # Code cannot branch to this label.
        self.based: bool = based

    def __repr__(self):
        return f"{self.label}:{self.dsp}:{self.length}:{self.name}"

    @property
    def dsp_hex(self) -> str:
        return f"{self.dsp:02X}"

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
        self_dict["dsp_hex"] = self.dsp_hex
        del self_dict["_branch"]
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

    def checked_lookup(self, label: str) -> Optional[LabelReference]:
        field = next(iter(label.split("&")))
        return self._symbol_table[field] if field in self._symbol_table else None

    def lookup(self, label: str) -> LabelReference:
        field = next(iter(label.split("&")))
        try:
            return self._symbol_table[field]
        except KeyError:
            raise NotFoundInSymbolTableError(label)

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
        updated_operand = operand.upper()
        data_list = re.findall(r"[CXHFDBZPAY]D?'[^']+'", updated_operand)
        value_list = list()
        if data_list:
            updated_operand = re.sub(r"[CXHFDBZPAY]D?'[^']+'", "~", updated_operand)
            for data in data_list:
                value = DataType(data[0], input=data[2:-1]).value
                value_list.insert(0, value)
        exp_list = re.split(r"([+*()/-])", updated_operand)
        if len(exp_list) == 1:
            if exp_list[0] == "~":
                return value_list.pop()
            return self._location_counter if exp_list[0] == "*" else self.evaluate(exp_list[0])
        exp_list = [expression for expression in exp_list if expression]
        if len(exp_list) >= 2 and exp_list[0] == "-" and exp_list[1].isdigit():
            exp_list.pop(0)
            exp_list[0] = f"-{exp_list[0]}"
        exp_list = [(index, expression) for index, expression in enumerate(exp_list)]
        parenthesis = [indexed_expression for indexed_expression in exp_list if indexed_expression[1] in "()"]
        exp_list = [indexed_expression for indexed_expression in exp_list if indexed_expression[1] not in "()"]
        eval_list = list()
        for index, (position, expression) in enumerate(exp_list):
            if expression in ("-", "+", "/") or (expression == "*" and index % 2 == 1):
                eval_list.append((position, expression))
            else:
                if expression == "~":
                    value = value_list.pop()
                elif expression == "*":
                    value = self._location_counter
                elif expression.isdigit() or (expression[0] == "-" and expression[1:].isdigit()):
                    value = str(int(expression))
                elif Register(expression).is_valid():
                    value = Register(expression).value
                else:
                    value = self.evaluate(expression)
                eval_list.append((position, str(value)))
        eval_list.extend(parenthesis)
        eval_list.sort(key=lambda item: item[0])
        eval_list = [expression for _, expression in eval_list]
        try:
            return_value = int(eval("".join(eval_list)))
        except SyntaxError:
            raise SyntaxError(operand)
        return return_value

    def is_based(self, operand: str) -> bool:
        if operand == "*":
            return True
        if not set("+*()/-").intersection(operand):
            return self.checked_lookup(operand).based if self.checked_lookup(operand) else False
        exp_list = re.split(r"([+*()/-])", operand)
        exp_list = [expression for expression in exp_list if expression and expression not in "()"]
        based = any(expression == "*" or
                    (self.checked_lookup(expression) is not None and self.checked_lookup(expression).based)
                    for index, expression in enumerate(exp_list) if index % 2 == 0)
        if based and "-" in operand:
            exp_list = [expression for index, expression in enumerate(exp_list)
                        if (index > 0 and exp_list[index - 1] == "-") or
                        (index < len(exp_list) - 1 and exp_list[index + 1]) == "-"]
            if (exp_list[0] == "*" or self.checked_lookup(exp_list[0])) and \
                    (exp_list[1] == "*" or self.checked_lookup(exp_list[1])):
                based = False
        return based

    def add_label(self, label: str, dsp: int, length: int, name: str, based: bool = True) -> LabelReference:
        label_ref = LabelReference(label, dsp, length, name, based)
        self._symbol_table[label] = label_ref
        index_label = name + str(dsp)
        if index_label not in self._index:
            self._index[index_label] = list()
        self._index[index_label].append((label, length))
        return label_ref
