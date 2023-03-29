from typing import List, Callable

from p5_v3.base_parser import Operators, GetIndex
from p5_v3.errors import ParserError
from p5_v3.operation_code import OperationCode


class OperandParser:

    def __init__(self, operand: str):
        self.operand: str = operand

    def split_operands(self) -> List[str]:
        operands: List[str] = list()
        start_index: int = int()
        closing_enclosure_index: int = -1
        for index, char in enumerate(self.operand):
            if index <= closing_enclosure_index:
                continue
            if char in {Operators.OPENING_PARENTHESIS, Operators.QUOTE}:
                closing_enclosure_index = GetIndex.of_closing_parenthesis(self.operand, index) if char == Operators.OPENING_PARENTHESIS \
                    else GetIndex.of_closing_quote(self.operand, index)
                if closing_enclosure_index == GetIndex.INVALID_ENCLOSURE:
                    raise ParserError("Operand -> Invalid closing enclosure while splitting operands.")
                continue
            if char == Operators.COMMA:
                operands.append(self.operand[start_index:index])
                start_index = index + 1
        operands.append(self.operand[start_index:len(self.operand)])
        return operands

    def parse(self, operation_code: str) -> list:
        operation: OperationCode = OperationCode(operation_code)
        if operation.is_parse_with_no_operands():
            return list()
        operands: List[str] = self.split_operands()
        parsers: List[Callable] = operation.get_operation_parsers()
        if operation.is_parse_based_on_operands():
            return [parsers[0](operand) for operand in operands if operand]
        # operation.is_parse_as_specified()
        if len(operands) != len(parsers):
            raise ParserError("Operand -> For parser as specified, the number of operands do not match.")
        return [parsers[index](operand) for index, operand in enumerate(operands) if operand]
