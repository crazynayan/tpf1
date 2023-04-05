from typing import List

from p5_v3.file import FilePreprocessor
from p5_v3.line import AssemblerLine, AssemblerLines
from p5_v3.operand import OperandParser
from p5_v3.operation_code import OperationCode


class ParsedLine:

    def __init__(self, line: AssemblerLine):
        self.label: str = line.label
        self.operation_code: OperationCode = OperationCode(line.operation_code)
        self.operands: list = OperandParser(line.operand).parse(self.operation_code)


class ParsedLines:

    def __init__(self, lines: List[AssemblerLine]):
        self.parsed_lines: List[ParsedLine] = [ParsedLine(line) for line in lines]

    def get_lines(self) -> List[ParsedLine]:
        return self.parsed_lines


class FileParser(ParsedLines):

    def __init__(self, filename: str):
        preprocessor: FilePreprocessor = FilePreprocessor(filename)
        assembler_lines: AssemblerLines = AssemblerLines(preprocessor.get_lines())
        super().__init__(assembler_lines.get_lines())
