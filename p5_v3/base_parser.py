from p5_v3.errors import AssemblyError

DATA_TYPES = {"X": 1, "C": 1, "H": 2, "F": 4, "D": 8, "FD": 8, "B": 1, "P": 1, "Z": 1, "A": 4, "Y": 2, "AD": 8, "V": 4,
              "S": 2}


class Operators:
    LOCATION_COUNTER = r"\*"
    PLUS = "+"
    MINUS = "-"
    PRODUCT = "*"
    DIVIDE = "/"
    UNDERSCORE = "_"
    DOLLAR = "$"
    HASH = "#"
    AT = "@"
    AMPERSAND = "&"
    QUOTE = "'"
    COMMA = ","
    OPENING_PARENTHESIS = "("
    CLOSING_PARENTHESIS = ")"
    LENGTH_SYMBOL = "L"
    PARENTHESIS = {OPENING_PARENTHESIS, CLOSING_PARENTHESIS}
    ENCLOSURES = PARENTHESIS.union({QUOTE})
    ARITHMETIC = {PLUS, MINUS, PRODUCT, DIVIDE}
    VALID_SYMBOLS = {AT, DOLLAR, HASH, AMPERSAND, UNDERSCORE}


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


class GetIndex:
    INVALID_CLOSING_ENCLOSURE = -99

    @classmethod
    def after_parenthesis_or_digits(cls, string: str, start_index: int) -> int:
        if start_index >= len(string):
            raise AssemblyError("GetIndex -> Index is beyond the length of string.")
        if string[start_index] == Operators.OPENING_PARENTHESIS:
            return cls.of_closing_parenthesis(string, start_index) + 1
        if string[start_index].isdigit():
            return cls.of_last_digit(string, start_index) + 1
        return cls.INVALID_CLOSING_ENCLOSURE

    @classmethod
    def after_parenthesis_or_quote(cls, string: str, start_index: int) -> int:
        if start_index >= len(string):
            raise AssemblyError("GetIndex -> Index is beyond the length of string.")
        if string[start_index] == Operators.OPENING_PARENTHESIS:
            return cls.of_closing_parenthesis(string, start_index) + 1
        if string[start_index] == Operators.QUOTE:
            return cls.of_closing_quote(string, start_index) + 1
        return cls.INVALID_CLOSING_ENCLOSURE

    @classmethod
    def of_closing_parenthesis(cls, string: str, start_index: int) -> int:
        if string[start_index] != Operators.OPENING_PARENTHESIS:
            raise AssemblyError("GetIndex -> Start index not at opening parenthesis.")
        nesting_level = 0
        for index in range(start_index, len(string)):
            if string[index] == Operators.OPENING_PARENTHESIS:
                nesting_level += 1
                continue
            if string[index] == Operators.CLOSING_PARENTHESIS:
                nesting_level -= 1
                if nesting_level == 0:
                    return index
        return cls.INVALID_CLOSING_ENCLOSURE

    @classmethod
    def of_closing_quote(cls, string: str, start_index: int) -> int:
        if string[start_index] != Operators.QUOTE:
            raise AssemblyError("GetIndex -> Start index not at opening quote.")
        for index in range(start_index + 1, len(string)):
            if string[index] == Operators.QUOTE:
                return index
        return cls.INVALID_CLOSING_ENCLOSURE

    @classmethod
    def of_last_digit(cls, string: str, start_index: int) -> int:
        if not string[start_index].isdigit():
            raise AssemblyError("of_last_digit -> Start index not at a digit.")
        for index in range(start_index, len(string) - start_index):
            if string[index].isdigit():
                continue
            return index - 1
        return len(string) - 1


def is_char_first_char_of_symbol(char: str) -> bool:
    return char.isalpha() or char in Operators.VALID_SYMBOLS


def is_char_part_of_symbol(char: str) -> bool:
    return char.isalnum() or char in Operators.VALID_SYMBOLS



