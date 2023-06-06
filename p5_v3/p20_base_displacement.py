from typing import List, Optional

from p5_v3.p01_errors import ParserError
from p5_v3.p11_base_parser import Operators, GetIndex
from p5_v3.p15_token_expression import Expression


def error_for_invalid_index(n: int) -> None:
    if not 1 <= n <= 3:
        raise ParserError


class BaseDisplacement:

    def __init__(self, string: str):
        self._expressions: List[Optional[Expression]] = [None, None, None]
        self.build(string)

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
        error_for_invalid_index(n)
        self._expressions[n - 1] = Expression(string)

    def is_nth_expression_present(self, n: int) -> bool:
        error_for_invalid_index(n)
        return self._expressions[n - 1] is not None

    def build(self, string: str):
        if Operators.OPENING_PARENTHESIS not in string:
            self.set_nth_expression(string, 1)
            return
        opening_parenthesis_index: int = string.index(Operators.OPENING_PARENTHESIS)
        if opening_parenthesis_index == 0:
            raise ParserError
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
