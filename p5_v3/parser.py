from typing import List

from p5_v3.errors import ParserError
from p5_v3.file import FilePreprocessor
from p5_v3.line import AssemblerLine, AssemblerLines
from p5_v3.operand import OperandParser
from p5_v3.operation_code import OperationCode


class ParsedLine:

    def __init__(self, line: AssemblerLine):
        self._label: str = line.label
        self.operation_code: OperationCode = OperationCode(line.operation_code)
        self.operands: list = OperandParser(line.operand).parse(self.operation_code)

    def __repr__(self):
        return f"{self._label}:{self.operation_code}:#{len(self.operands)}"

    @property
    def label(self) -> str:
        return next(iter(self._label.split("&")))

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


class ParsedLines:

    def __init__(self, lines: List[AssemblerLine]):
        self.parsed_lines: List[ParsedLine] = [ParsedLine(line) for line in lines]

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
