from typing import List

from p5_v3.p01_errors import ParserError
from p5_v3.p11_base_parser import Operators
from p5_v3.p16_file import FilePreprocessor, StreamPreprocessor
from p5_v3.p17_line import AssemblerLine, AssemblerLines
from p5_v3.p22_format import GenericFormat
from p5_v3.p23_operation_code_format import get_operation_format, check_operation_code_validity


class ParsedLine:

    def __init__(self, line: AssemblerLine):
        self.location_counter: int = int()
        self._label: str = line.label
        self.format: GenericFormat = get_operation_format(line.operation_code)(line.operand)
        self.operation_code: str = line.operation_code

    def __repr__(self):
        return self.pretty_print(with_location_counter=True)

    def pretty_print(self, with_location_counter=True) -> str:
        string = str()
        if with_location_counter:
            string += f"{self.location_counter:08X}:"
        string += f"{self._label:8} "
        string += f"{self.operation_code:5} "
        string += Operators.COMMA.join(
            [self.format.get_nth_operand(n).pretty_print() for n in range(1, self.format.number_of_operands() + 1)])
        return string

    @property
    def label(self) -> str:
        return self._label.split("&")[0]

    def get_macro_arguments(self):
        return self.format.get_nth_operand(1)

    def is_label_present(self) -> bool:
        return bool(self.label)

    def set_location_counter(self, location_counter: int):
        self.location_counter = location_counter


class ParsedLines:

    def __init__(self, lines: List[AssemblerLine]):
        if not lines:
            raise ParserError
        operation_codes: List[str] = [line.operation_code for line in lines]
        operation_codes_validity_status: List[bool] = check_operation_code_validity(operation_codes)
        if not all(operation_codes_validity_status):
            invalid_lines: List[AssemblerLine] = [lines[index] for index, status in enumerate(operation_codes_validity_status)
                                                  if status is False]
            for line in invalid_lines:
                print(line.pretty_print())
            raise ParserError
        self.parsed_lines: List[ParsedLine] = [ParsedLine(line) for line in lines]

    def __repr__(self) -> str:
        return self.pretty_print()

    def pretty_print(self) -> str:
        return "\n".join([parsed_line.pretty_print() for parsed_line in self.parsed_lines])

    def get_lines(self) -> List[ParsedLine]:
        return self.parsed_lines

    def get_parsed_line(self, label) -> ParsedLine:
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
