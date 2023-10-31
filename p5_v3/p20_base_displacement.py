from typing import List, Optional, Tuple

from p5_v3.p01_errors import ParserError
from p5_v3.p11_base_parser import Operators, GetIndex
from p5_v3.p15_token_expression import Expression


class BaseDisplacementExpression:
    VALID_COUNT: Tuple[int] = (1, 2, 3)

    @classmethod
    def error_for_invalid_index(cls, n: int) -> None:
        if n not in cls.VALID_COUNT:
            raise ParserError


class BaseDisplacement:

    def __init__(self, string: str):
        self._expressions: List[Optional[Expression]] = [None, None, None]
        self.build(string)

    def __repr__(self):
        return self.pretty_print()

    def pretty_print(self) -> str:
        string = str()
        if not self.is_nth_expression_present(1):
            return string
        string += self.expression1.pretty_print()
        if not self.is_nth_expression_present(2) and not self.is_nth_expression_present(3):
            return string
        string += Operators.OPENING_PARENTHESIS
        if self.is_nth_expression_present(2):
            string += self.expression2.pretty_print()
        string += Operators.COMMA
        if self.is_nth_expression_present(3):
            string += self.expression3.pretty_print()
        string += Operators.CLOSING_PARENTHESIS
        return string

    @property
    def expression1(self) -> Expression:
        return self._expressions[0]

    @property
    def expression2(self) -> Expression:
        return self._expressions[1]

    @property
    def expression3(self) -> Expression:
        return self._expressions[2]

    def set_nth_expression(self, string: str, n: int) -> None:
        BaseDisplacementExpression.error_for_invalid_index(n)
        self._expressions[n - 1] = Expression(string)

    def is_nth_expression_present(self, n: int) -> bool:
        BaseDisplacementExpression.error_for_invalid_index(n)
        return self._expressions[n - 1] is not None

    def find_end_index_of_first_operand(self, string: str, from_index: int) -> int:
        closing_parenthesis_index: int = GetIndex.of_closing_parenthesis(string, from_index)
        if closing_parenthesis_index == GetIndex.INVALID_ENCLOSURE:
            raise ParserError
        if closing_parenthesis_index + 1 == len(string):
            return closing_parenthesis_index
        if Operators.OPENING_PARENTHESIS not in string[closing_parenthesis_index + 1:]:
            return len(string) - 1
        current_index = closing_parenthesis_index + 1
        if string[current_index] == Operators.OPENING_PARENTHESIS:
            return closing_parenthesis_index
        opening_parenthesis_index: int = string[current_index:].index(Operators.OPENING_PARENTHESIS) + current_index
        return self.find_end_index_of_first_operand(string, opening_parenthesis_index)

    def build(self, string: str):
        if Operators.OPENING_PARENTHESIS not in string:
            self.set_nth_expression(string, 1)
            return
        opening_parenthesis_index: int = string.index(Operators.OPENING_PARENTHESIS)
        if opening_parenthesis_index == 0:
            end_index_of_first_operand: int = self.find_end_index_of_first_operand(string, 0)
            if end_index_of_first_operand == len(string) - 1:
                self.set_nth_expression(string[:end_index_of_first_operand + 1], 1)
                return
            opening_parenthesis_index = end_index_of_first_operand + 1
        self.set_nth_expression(string[:opening_parenthesis_index], 1)
        closing_parenthesis_index: int = GetIndex.of_closing_parenthesis(string, opening_parenthesis_index)
        if closing_parenthesis_index == GetIndex.INVALID_ENCLOSURE:
            raise ParserError
        within_parenthesis: str = string[opening_parenthesis_index + 1:closing_parenthesis_index]
        if Operators.COMMA not in within_parenthesis:
            self.set_nth_expression(within_parenthesis, 2)
            return
        comma_index: int = within_parenthesis.index(Operators.COMMA)
        if comma_index != 0:
            self.set_nth_expression(within_parenthesis[:comma_index], 2)
        if comma_index < len(within_parenthesis) - 1:  # comma is not at the end
            self.set_nth_expression(within_parenthesis[comma_index + 1:], 3)
        return
