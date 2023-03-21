from typing import List

from p5_v3.errors import ParserError


class Operators:
    LOCATION_COUNTER = r"\*"
    MAX_LOCATION_COUNTER = r"\**"
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
    SPACE = " "
    OPENING_PARENTHESIS = "("
    CLOSING_PARENTHESIS = ")"
    LENGTH_SYMBOL = "L"
    PARENTHESIS = {OPENING_PARENTHESIS, CLOSING_PARENTHESIS}
    ENCLOSURES = PARENTHESIS.union({QUOTE})
    ARITHMETIC = {PLUS, MINUS, PRODUCT, DIVIDE}
    VALID_SYMBOLS = {AT, DOLLAR, HASH, AMPERSAND, UNDERSCORE}


class GetIndex:
    INVALID_ENCLOSURE = -99

    @classmethod
    def after_parenthesis_or_digits(cls, string: str, start_index: int) -> int:
        if start_index >= len(string):
            return cls.INVALID_ENCLOSURE
        if string[start_index] == Operators.OPENING_PARENTHESIS:
            return cls.of_closing_parenthesis(string, start_index) + 1
        if string[start_index].isdigit():
            return cls.of_last_digit(string, start_index) + 1
        return cls.INVALID_ENCLOSURE

    @classmethod
    def after_parenthesis_or_quote(cls, string: str, start_index: int) -> int:
        if start_index >= len(string):
            return cls.INVALID_ENCLOSURE
        if string[start_index] == Operators.OPENING_PARENTHESIS:
            return cls.of_closing_parenthesis(string, start_index) + 1
        if string[start_index] == Operators.QUOTE:
            return cls.of_closing_quote(string, start_index) + 1
        return cls.INVALID_ENCLOSURE

    @classmethod
    def of_closing_parenthesis(cls, string: str, start_index: int) -> int:
        if string[start_index] != Operators.OPENING_PARENTHESIS:
            raise ParserError("GetIndex -> Start index not at opening parenthesis.")
        nesting_level = 0
        for index in range(start_index, len(string)):
            if string[index] == Operators.OPENING_PARENTHESIS:
                nesting_level += 1
                continue
            if string[index] == Operators.CLOSING_PARENTHESIS:
                nesting_level -= 1
                if nesting_level == 0:
                    return index
        return cls.INVALID_ENCLOSURE

    @classmethod
    def of_closing_quote(cls, string: str, start_index: int) -> int:
        if string[start_index] != Operators.QUOTE:
            raise ParserError("GetIndex -> Start index not at opening quote.")
        for index in range(start_index + 1, len(string)):
            if string[index] == Operators.QUOTE:
                return index
        return cls.INVALID_ENCLOSURE

    @classmethod
    def of_last_digit(cls, string: str, start_index: int) -> int:
        if not string[start_index].isdigit():
            raise ParserError("of_last_digit -> Start index not at a digit.")
        for index in range(start_index, len(string) - start_index):
            if string[index].isdigit():
                continue
            return index - 1
        return len(string) - 1


def is_char_first_char_of_symbol(char: str) -> bool:
    return char.isalpha() or char in Operators.VALID_SYMBOLS


def is_char_part_of_symbol(char: str) -> bool:
    return char.isalnum() or char in Operators.VALID_SYMBOLS


def split_operands(operand: str) -> List[str]:
    operands: List[str] = list()
    start_index: int = int()
    closing_enclosure_index: int = -1
    for index, char in enumerate(operand):
        if index <= closing_enclosure_index:
            continue
        if char in {Operators.OPENING_PARENTHESIS, Operators.QUOTE}:
            closing_enclosure_index = GetIndex.of_closing_parenthesis(operand, index) if char == Operators.OPENING_PARENTHESIS else \
                GetIndex.of_closing_quote(operand, index)
            if closing_enclosure_index == GetIndex.INVALID_ENCLOSURE:
                raise ParserError("split_operands -> Invalid closing enclosure.")
            continue
        if char == Operators.COMMA:
            operands.append(operand[start_index:index])
            start_index = index + 1
    operands.append(operand[start_index:len(operand)])
    return operands
