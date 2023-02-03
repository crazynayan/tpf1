from types import SimpleNamespace
from typing import Optional, List


class AssemblyError(Exception):
    pass


LOCATION_COUNTER = "\*"
OPERATORS = SimpleNamespace()
OPERATORS.ARITHMETIC = {"*", "+", "-", "/"}
OPERATORS.PARENTHESIS = {"(", ")"}
OPERATORS.QUOTE = "'"
OPERATORS.ENCLOSURES = OPERATORS.PARENTHESIS.add(OPERATORS.QUOTE)
REGISTERS = SimpleNamespace()
REGISTERS.TO_VALUE = {"R0": 0, "R00": 0, "RAC": 0, "R1": 1, "R01": 1, "RG1": 1}
REGISTERS.TO_SYMBOL = {"0": "R0", "1": "R1"}
DATA_PREFIX = "'"


class Token:

    def __init__(self, string: str):
        if not string:
            raise AssemblyError("Token -> token cannot be empty.")
        if string[0] == DATA_PREFIX and len(string) == 1:
            raise AssemblyError("Token -> token cannot be empty data.")
        self._string: str = string

    def __repr__(self) -> str:
        return self._string

    def evaluate(self, *, symbol_table=None, location_counter=None, data_type=None) -> str:
        if self.is_decimal():
            return str(self.get_value_from_decimal())
        if self.is_register():
            return str(self.get_value_from_register())
        if self.is_arithmetic_operator() or self.is_parenthesis():
            return self._string
        if self.is_symbol():
            if not symbol_table:
                raise AssemblyError("Token -> Symbol Table not provided to evaluate a symbol.")
            return str(self.get_value_from_symbol(symbol_table))
        if self.is_data():
            if not data_type:
                raise AssemblyError("Token -> Data Type not provided to evaluate a data.")
            return str(self.get_value_from_data(data_type))
        if self.is_location_counter():
            return str(location_counter)
        raise AssemblyError("Token -> Cannot evaluate token of unknown type.")

    def is_decimal(self) -> bool:
        return self._string.isdigit()

    def get_value_from_decimal(self) -> int:
        try:
            return int(self._string)
        except ValueError:
            raise AssemblyError("Token -> token is not decimal.")

    def is_register(self) -> bool:
        return self._string in REGISTERS.TO_VALUE

    def get_value_from_register(self) -> int:
        try:
            return REGISTERS.TO_VALUE[self._string]
        except KeyError:
            raise AssemblyError("Token -> token is not register.")

    def is_symbol(self) -> bool:
        if self.is_register():
            return False
        return self._string[0].isalpha()

    def get_value_from_symbol(self, symbol_table) -> int:
        pass

    def is_data(self) -> bool:
        return self._string[0] == DATA_PREFIX

    @property
    def data(self) -> str:
        if self._string[0] != DATA_PREFIX:
            raise AssemblyError("Token - token is not data.")
        return self._string[1:]

    def get_value_from_data(self, data_type) -> int:
        pass

    def is_location_counter(self):
        return self._string == LOCATION_COUNTER

    def is_arithmetic_operator(self):
        return self._string in OPERATORS.ARITHMETIC

    def is_parenthesis(self):
        return self._string in OPERATORS.PARENTHESIS


class Expression:

    def __init__(self):
        self.tokens: List[Token] = list()
        self.self_defined_term: Optional[SelfDefinedTerm] = None

    def has_arithmetic_operator(self) -> bool:
        return any(token for token in self.tokens if token.is_arithmetic_operator())

    def has_symbol(self) -> bool:
        return any(token for token in self.tokens if token.is_symbol())


class SelfDefinedTerm:

    def __init__(self):
        self.duplication_factor: Optional[Expression] = None
        self.data_type: str = str()
        self.length: Optional[Expression] = None
        self.values: List[Expression] = list()
