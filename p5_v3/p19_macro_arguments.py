from typing import List, Optional

from p5_v3.p01_errors import ParserError, MacroArgumentError
from p5_v3.p11_base_parser import Operators, GetIndex, split_operand


class KeyValue:

    def __init__(self, string: str):
        self.key: str = str()
        self.value: str = str()
        self.macro_arguments: Optional[MacroArguments] = None
        if not string:
            raise ParserError
        self.build(string)

    def __repr__(self):
        return self.pretty_print()

    def is_key_only(self):
        return not self.value and not self.macro_arguments

    def is_key_value(self):
        return bool(self.value) and not self.macro_arguments

    def has_macro_arguments(self):
        return bool(self.macro_arguments) and not self.value

    def build(self, string: str):
        if Operators.NAMED_MACRO_ARGUMENTS_DELIMITER not in string:
            self.key = string
            return
        delimiter_index: int = string.index(Operators.NAMED_MACRO_ARGUMENTS_DELIMITER)
        self.key = string[:delimiter_index]
        if delimiter_index + 1 == len(string):
            return
        if string[delimiter_index + 1] != Operators.OPENING_PARENTHESIS:
            self.value = string[delimiter_index + 1:]
            return
        closing_parenthesis_index: int = GetIndex.of_closing_parenthesis(string, delimiter_index + 1)
        # if closing parenthesis not found OR closing parenthesis is NOT the last char OR there are no char between opening & closing parenthesis
        if closing_parenthesis_index == GetIndex.INVALID_ENCLOSURE or closing_parenthesis_index + 1 != len(string) or \
                delimiter_index + 2 == closing_parenthesis_index:
            raise ParserError
        sub_key_list: List[str] = split_operand(string[delimiter_index + 2:closing_parenthesis_index])
        self.macro_arguments: MacroArguments = MacroArguments(sub_key_list)
        return

    def pretty_print(self) -> str:
        string: str = self.key
        if self.is_key_only():
            return string
        if self.is_key_value():
            string += f"{Operators.NAMED_MACRO_ARGUMENTS_DELIMITER}{self.value}"
            return string
        string += f"{Operators.NAMED_MACRO_ARGUMENTS_DELIMITER}({self.macro_arguments.pretty_print()})"
        return string


class MacroArguments:

    def __init__(self, strings: List[str]):
        self.key_values: List[KeyValue] = list()
        if not strings or all(string.strip() == str() for string in strings):
            raise ParserError
        self.key_values: List[KeyValue] = [KeyValue(string) for string in strings if string]

    def __repr__(self):
        return self.pretty_print()

    def get_key_list(self) -> List[str]:
        return [key_value.key for key_value in self.key_values]

    def get_nth_key(self, n: int) -> str:
        key_list = self.get_key_list()
        if n < 1 or n > len(key_list):
            raise MacroArgumentError
        return key_list[n - 1]

    def get_number_of_keys(self) -> int:
        return len(self.key_values)

    def get_key_value(self, key: str) -> KeyValue:
        try:
            return next(key_value for key_value in self.key_values if key_value.key == key)
        except StopIteration:
            raise MacroArgumentError

    def is_key_present(self, key: str) -> bool:
        return any(key_value.key == key for key_value in self.key_values)

    def is_key_with_value(self, key: str):
        return self.get_key_value(key).is_key_value()

    def is_key_only(self, key: str):
        return self.get_key_value(key).is_key_only()

    def is_key_with_macro_arguments(self, key: str):
        return self.get_key_value(key).has_macro_arguments()

    def get_value(self, key: str) -> str:
        key_value: KeyValue = self.get_key_value(key)
        if not key_value.is_key_value():
            raise MacroArgumentError
        return key_value.value

    def get_macro_arguments(self, key: str) -> 'MacroArguments':
        key_value: KeyValue = self.get_key_value(key)
        if not key_value.has_macro_arguments():
            raise MacroArgumentError
        return key_value.macro_arguments

    def pretty_print(self):
        return Operators.COMMA.join([key_value.pretty_print() for key_value in self.key_values])
