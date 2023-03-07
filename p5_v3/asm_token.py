from types import SimpleNamespace

from p5_v3.errors import AssemblyError

REGISTERS = SimpleNamespace()
REGISTERS.TO_VALUE = {"R0": 0, "R00": 0, "RAC": 0, "R1": 1, "R01": 1, "RG1": 1}
REGISTERS.TO_SYMBOL = {"0": "R0", "1": "R1"}
DATA_PREFIX = "'"
DATA_TYPES = {"X": 1, "C": 1, "H": 2, "F": 4, "D": 8, "FD": 8, "B": 1, "P": 1, "Z": 1, "A": 4, "Y": 2, "AD": 8, "V": 4,
              "S": 2}


class Operators:
    LOCATION_COUNTER = "\*"
    PLUS = "+"
    MINUS = "-"
    PRODUCT = "*"
    DIVIDE = "/"
    UNDERSCORE = "_"
    DOLLAR = "$"
    HASH = "#"
    AT = "@"
    AMPERSAND = "&"
    VALID_SYMBOLS = {AT, DOLLAR, HASH, AMPERSAND, UNDERSCORE}
    QUOTE = "'"
    COMMA = ","
    OPENING_PARENTHESIS = "("
    CLOSING_PARENTHESIS = ")"
    PARENTHESIS = {OPENING_PARENTHESIS, CLOSING_PARENTHESIS}
    ENCLOSURES = PARENTHESIS.union({QUOTE})
    ARITHMETIC = {PLUS, MINUS, PRODUCT, DIVIDE}
    LENGTH_SYMBOL = "L"


def is_data_type(input_string: str) -> bool:
    try:
        get_data_type(input_string)
        return True
    except AssemblyError:
        return False


def get_data_type(input_string: str) -> str:
    string = input_string.upper()
    if len(string) >= 2 and string[:2] in DATA_TYPES:
        return string[:2]
    if len(string) >= 1 and string[0] in DATA_TYPES:
        return string[0]
    raise AssemblyError("get_data_type -> Input string is not a data type.")


def get_data_type_length(string: str) -> str:
    try:
        return DATA_TYPES[string]
    except KeyError:
        raise AssemblyError("get_data_type_length -> Input string is not a data type.")


def get_index_after_parenthesis_or_digits(string: str, start_index: int) -> int:
    if start_index >= len(string):
        raise AssemblyError("get_index_after_parenthesis_or_digits -> Index is beyond the length of string.")
    if string[start_index] == Operators.OPENING_PARENTHESIS:
        return get_index_of_closing_parenthesis(string, start_index) + 1
    if string[start_index].isdigit():
        return get_index_of_last_digit(string, start_index) + 1
    return 0


def get_index_of_closing_parenthesis(string: str, start_index: int) -> int:
    if string[start_index] != Operators.OPENING_PARENTHESIS:
        raise AssemblyError("get_index_of_closing_parenthesis -> Start index not at opening parenthesis.")
    nesting_level = 0
    for index in range(start_index, len(string)):
        if string[index] == Operators.OPENING_PARENTHESIS:
            nesting_level += 1
            continue
        if string[index] == Operators.CLOSING_PARENTHESIS:
            nesting_level -= 1
            if nesting_level == 0:
                return index
    raise AssemblyError("get_index_of_closing_parenthesis -> Matching closing parenthesis not found.")


def get_index_of_last_digit(string: str, start_index: int) -> int:
    if not string[start_index].isdigit():
        raise AssemblyError("get_index_of_last_digit -> Start index not at a digit.")
    for index in range(start_index, len(string) - start_index):
        if string[index].isdigit():
            continue
        return index - 1
    return len(string) - 1


class Token:

    def __init__(self, string: str, data: bool = False):
        if not string:
            raise AssemblyError("Token -> token cannot be empty.")
        if string[0] == DATA_PREFIX and len(string) == 1:
            raise AssemblyError("Token -> token cannot be empty data.")
        self._string: str = string
        if data:
            self._string = f"{DATA_PREFIX}string"

    def __repr__(self) -> str:
        return self._string

    def evaluate_to_str(self, *, symbol_table=None, location_counter=None, data_type=None) -> str:
        if self.is_arithmetic_operator() or self.is_parenthesis():
            return self._string
        return str(self.evaluate(symbol_table=symbol_table, location_counter=location_counter, data_type=data_type))

    def evaluate(self, *, symbol_table=None, location_counter=None, data_type=None) -> int:
        if self.is_decimal():
            return self.get_value_from_decimal()
        if self.is_register():
            return self.get_value_from_register()
        if self.is_symbol():
            if not symbol_table:
                raise AssemblyError("Token -> Symbol Table not provided to evaluate a symbol.")
            return self.get_value_from_symbol(symbol_table)
        if self.is_data():
            if not data_type:
                raise AssemblyError("Token -> Data Type not provided to evaluate a data.")
            return self.get_value_from_data(data_type)
        if self.is_location_counter():
            return location_counter
        raise AssemblyError("Token -> Cannot evaluate token.")

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
        return self._string[0].isalpha() or self._string[0] in Operators.VALID_SYMBOLS

    def get_value_from_symbol(self, symbol_table) -> int:
        return 0

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
        return self._string == Operators.LOCATION_COUNTER

    def is_arithmetic_operator(self):
        return self._string in Operators.ARITHMETIC

    def is_parenthesis(self):
        return self._string in Operators.PARENTHESIS

    def is_quote(self):
        return self._string == Operators.QUOTE

    def is_comma(self):
        return self._string == Operators.COMMA
