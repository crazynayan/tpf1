from typing import List, Optional

from p5_v3.p01_errors import ParserError, MacroArgumentError
from p5_v3.p11_base_parser import Operators, GetIndex, split_operand


class KeyValue:

    def __init__(self, string: str):
        self.key: str = str()
        self.value: str = str()
        self.values: Optional[MacroArguments] = None
        if not string:
            raise ParserError
        self.build(string)

    def is_key_only(self):
        return not self.value and not self.values

    def is_key_value(self):
        return bool(self.value) and not self.values

    def is_key_values(self):
        return bool(self.values) and not self.value

    def build(self, string: str):
        if Operators.NAMED_MACRO_ARGUMENTS_DELIMITER not in string:
            self.key = string
            return
        delimiter_index: int = string.index(Operators.NAMED_MACRO_ARGUMENTS_DELIMITER)
        if delimiter_index == len(string):
            raise ParserError
        self.key = string[:delimiter_index]
        if string[delimiter_index + 1] != Operators.OPENING_PARENTHESIS:
            self.value = string[delimiter_index + 1:]
            return
        closing_parenthesis_index: int = GetIndex.of_closing_parenthesis(string, delimiter_index + 1)
        if closing_parenthesis_index == GetIndex.INVALID_ENCLOSURE or closing_parenthesis_index + 1 != len(string) or \
                delimiter_index + 2 == closing_parenthesis_index:
            raise ParserError
        sub_key_list: List[str] = split_operand(string[delimiter_index + 2:closing_parenthesis_index])
        self.values: MacroArguments = MacroArguments(sub_key_list)
        return


class MacroArguments:

    def __init__(self, strings: List[str]):
        self.key_values: List[KeyValue] = list()
        if not strings or all(string.strip() == str() for string in strings):
            raise ParserError
        self.key_values: List[KeyValue] = [KeyValue(string) for string in strings if string]

    def get_key_list(self) -> List[str]:
        return [key_value.key for key_value in self.key_values]

    def get_nth_key(self, n: int) -> str:
        key_list = self.get_key_list()
        if n < 1 or n > len(key_list):
            raise MacroArgumentError
        return key_list[n - 1]

    def get_value(self, key: str) -> str:
        try:
            key_value: KeyValue = next(key_value for key_value in self.key_values if key_value.key == key)
        except StopIteration:
            raise MacroArgumentError
        if not key_value.is_key_value():
            raise MacroArgumentError
        return key_value.value
