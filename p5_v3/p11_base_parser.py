from typing import List

from p5_v3.p01_errors import ParserError


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
    LENGTH_ATTRIBUTE = "L"
    TYPE_ATTRIBUTE = "T"
    SCALING_ATTRIBUTE = "S"
    INTEGER_ATTRIBUTE = "I"
    COUNT_ATTRIBUTE = "K"
    NUMBER_ATTRIBUTE = "N"
    DEFINED_ATTRIBUTE = "D"
    OPERATION_CODE_ATTRIBUTE = "O"
    LITERAL_IDENTIFIER = "="
    NAMED_MACRO_ARGUMENTS_DELIMITER = "="
    ATTRIBUTES = {LENGTH_ATTRIBUTE, TYPE_ATTRIBUTE, SCALING_ATTRIBUTE, INTEGER_ATTRIBUTE, COUNT_ATTRIBUTE, NUMBER_ATTRIBUTE,
                  DEFINED_ATTRIBUTE, OPERATION_CODE_ATTRIBUTE}
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


def split_operand(string: str) -> List[str]:
    operands: List[str] = list()
    start_index: int = int()
    closing_enclosure_index: int = -1
    for index, char in enumerate(string):
        if index <= closing_enclosure_index:
            continue
        if char in {Operators.OPENING_PARENTHESIS, Operators.QUOTE}:
            closing_enclosure_index = GetIndex.of_closing_parenthesis(string, index) if char == Operators.OPENING_PARENTHESIS \
                else GetIndex.of_closing_quote(string, index)
            if closing_enclosure_index == GetIndex.INVALID_ENCLOSURE:
                raise ParserError("Operand -> Invalid closing enclosure while splitting operands.")
            continue
        if char == Operators.COMMA:
            operands.append(string[start_index:index])
            start_index = index + 1
    operands.append(string[start_index:len(string)])
    return operands


def is_segment_name(seg_name: str) -> bool:
    if len(seg_name) != 4:
        return False
    if not seg_name.isalnum():
        return False
    if not seg_name[0].isalpha():
        return False
    return True
