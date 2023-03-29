from p5_v3.line import AssemblerLine, AssemblerLines
from p5_v3.operand import OperandParser
from p5_v3.operation_code import OperationCode


class ParsedLine:

    def __init__(self, line: AssemblerLine):
        self.label: str = line.label
        self.operation_code: OperationCode = OperationCode(line.operation_code)
        self.operands: list = OperandParser(line.operand).parse(self.operation_code)


class ParsedLines:

    def __init__(self, lines: AssemblerLines):
        self.parsed_lines: list = [ParsedLine(line) for line in lines.lines]
