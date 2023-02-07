from typing import Optional, List

from p5_v3.token import Token, AssemblyError, is_data_type, get_data_type, \
    get_index_after_parenthesis_or_digits


class Expression:

    def __init__(self):
        self.tokens: List[Token] = list()
        self.self_defined_term: Optional[SelfDefinedTerm] = None

    def has_arithmetic_operator(self) -> bool:
        return any(token for token in self.tokens if token.is_arithmetic_operator())

    def has_symbol_or_location_counter(self) -> bool:
        return any(token for token in self.tokens if token.is_symbol() or token.is_location_counter())


class SelfDefinedTerm:

    def __init__(self):
        self.duplication_factor: Optional[Expression] = None
        self.data_type: str = str()
        self.length: Optional[Expression] = None
        self.opening_enclosure: Optional[Token] = None
        self.values: List[Expression] = list()

    def build(self, string: str):
        if not string:
            raise AssemblyError("SelfDefinedTerm -> Input string cannot be empty.")
        data_type_index = get_index_after_parenthesis_or_digits(string, 0)
        if not is_data_type(string[data_type_index:]):
            raise AssemblyError("SelfDefinedTerm -> The string does not have a valid data type.")
        if data_type_index > 0:
            self.build_duplication_factor(string[:data_type_index])
        self.data_type = get_data_type(string[data_type_index])
        length_index = data_type_index + len(self.data_type)
        if string[length_index] == "L":
            value_index = get_index_after_parenthesis_or_digits(string, length_index + 1)
            if value_index == 0:
                raise AssemblyError("SelfDefinedTerm -> Length after L is not specified.")
            self.build_length(string[length_index + 1:value_index])
        else:
            value_index = length_index
        if value_index < len(string):
            self.build_values(string[value_index:])
        return

    def build_duplication_factor(self, string: str):
        pass

    def build_length(self, string: str):
        pass

    def build_values(self, string: str):
        pass
