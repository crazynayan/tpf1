from typing import List, Callable

from p5_v3.p01_errors import ParserError
from p5_v3.p11_base_parser import Operators, split_operand
from p5_v3.p16_file import FilePreprocessor, StreamPreprocessor
from p5_v3.p17_line import AssemblerLine, AssemblerLines
from p5_v3.p21_operation_code import OperationCode


class ParsedLine:

    def __init__(self, line: AssemblerLine):
        self.location_counter: int = int()
        self._label: str = line.label
        self.operation_code: OperationCode = OperationCode(line.operation_code)
        self.operands = self.parse_operand(line.operand)

    def __repr__(self):
        return self.pretty_print(with_location_counter=True)

    def pretty_print(self, with_location_counter=True) -> str:
        string = str()
        if with_location_counter:
            string += f"{self.location_counter:08X}:"
        string += f"{self._label:8} "
        string += f"{self.operation_code.pretty_print():5} "
        string += Operators.COMMA.join([operand.pretty_print() for operand in self.operands])
        return string

    @property
    def label(self) -> str:
        return next(iter(self._label.split("&")))

    def get_macro_arguments(self):
        return self.get_nth_operand(1)

    def is_label_present(self) -> bool:
        return bool(self.label)

    def has_no_operands(self) -> bool:
        return not bool(self.operands)

    def number_of_operands(self) -> int:
        return len(self.operands)

    def get_nth_operand(self, n: int):
        try:
            return self.operands[n - 1]
        except IndexError:
            raise ParserError("ParsedLine -> Invalid index of operand requested.")

    def set_location_counter(self, location_counter: int):
        self.location_counter = location_counter

    def parse_operand(self, operand: str) -> list:
        if self.operation_code.is_parse_with_no_operands():
            return list()
        operands: List[str] = split_operand(operand)
        parsers: List[Callable] = self.operation_code.get_operation_parsers()
        if self.operation_code.is_parse_based_on_operands():
            return [parsers[0](operand) for operand in operands if operand]
        # Operation code indicates parse as specified
        if len(operands) != len(parsers):
            raise ParserError("Operand -> For parser as specified, the number of operands do not match.")
        # Empty operands are ignored. An only comma is equated to no operand.
        return [parsers[index](operand) for index, operand in enumerate(operands) if operand]


class ParsedLines:

    def __init__(self, lines: List[AssemblerLine]):
        self.parsed_lines: List[ParsedLine] = [ParsedLine(line) for line in lines]

    def __repr__(self):
        return self.pretty_print()

    def pretty_print(self):
        return "\n".join([parsed_line.pretty_print() for parsed_line in self.parsed_lines])

    def get_lines(self) -> List[ParsedLine]:
        return self.parsed_lines

    def get_parsed_line(self, label):
        if not label:
            raise ParserError
        try:
            return next(parsed_line for parsed_line in self.parsed_lines if parsed_line.label == label)
        except StopIteration:
            raise ParserError


class FileParser(ParsedLines):

    def __init__(self, filename: str):
        preprocessor: FilePreprocessor = FilePreprocessor(filename)
        assembler_lines: AssemblerLines = AssemblerLines(preprocessor.get_lines())
        super().__init__(assembler_lines.get_lines())


class StreamParser(ParsedLines):

    def __init__(self, buffer: str):
        preprocessor: StreamPreprocessor = StreamPreprocessor(buffer)
        assembler_lines: AssemblerLines = AssemblerLines(preprocessor.get_lines())
        super().__init__(assembler_lines.get_lines())