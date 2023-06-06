from typing import Tuple, List, Optional

from p5_v3.p01_errors import ParserError
from p5_v3.p11_base_parser import Operators


class AssemblerLine:
    LABEL_START = 0
    CONTINUATION_START = 71
    CONTINUING_START = 15
    COMMENTED_OUT_CHARS = {"*", "."}

    def __init__(self, line):
        self.line: str = line
        self.operand_accumulator: str = str()

    def __repr__(self):
        return f"{self.label}:{self.operation_code}:{self.operand}"

    def get_next_space(self, start_index: int) -> int:
        for index, char in enumerate(self.line[start_index:]):
            if char == Operators.SPACE:
                return index + start_index
        raise ParserError("AssemblerLine -> Next space not found.")

    def get_next_non_space(self, start_index: int) -> int:
        for index, char in enumerate(self.line[start_index:]):
            if char != Operators.SPACE:
                return index + start_index
        raise ParserError("AssemblerLine -> Next non space not found.")

    def is_label_present(self) -> bool:
        return self.line[self.LABEL_START] != Operators.SPACE and self.line[self.LABEL_START] not in self.COMMENTED_OUT_CHARS

    @property
    def label_end(self) -> int:
        try:
            return self.get_next_space(self.LABEL_START)
        except ParserError:
            return len(self.line)

    @property
    def label(self) -> str:
        return self.line[:self.label_end]

    @property
    def operation_code_start(self) -> int:
        try:
            return self.get_next_non_space(self.label_end)
        except ParserError:
            return len(self.line)

    @property
    def operation_code_end(self) -> int:
        try:
            return self.get_next_space(self.operation_code_start)
        except ParserError:
            return len(self.line)

    @property
    def operation_code(self) -> str:
        return self.line[self.operation_code_start: self.operation_code_end]

    def is_commented_out(self) -> bool:
        return self.line[self.LABEL_START] in self.COMMENTED_OUT_CHARS

    def is_continuation_present(self) -> bool:
        return len(self.line) > self.CONTINUATION_START and self.line[self.CONTINUATION_START] != Operators.SPACE

    def get_operand_info(self, continuing: bool, inside_quote: bool, previous_line_ending_with_l: bool,
                         parenthesis_nesting_level: int) -> Tuple[str, bool, int]:
        try:
            operand_start = self.CONTINUING_START if continuing else self.get_next_non_space(self.operation_code_end)
        except ParserError:
            return str(), bool(), int()
        if operand_start >= self.CONTINUATION_START:
            return str(), bool(), int()
        is_inside_quote = inside_quote
        nesting_level = parenthesis_nesting_level
        operand_end = self.CONTINUATION_START
        for index, char in enumerate(self.line[operand_start:self.CONTINUATION_START]):
            possible_length_attribute = previous_line_ending_with_l
            if index > 0:
                possible_length_attribute = self.line[operand_start + index - 1] in Operators.ATTRIBUTES
            if not is_inside_quote and char == Operators.QUOTE and not possible_length_attribute:
                is_inside_quote = True
                continue
            if is_inside_quote and char == Operators.QUOTE:
                is_inside_quote = False
                continue
            if char == Operators.OPENING_PARENTHESIS:
                nesting_level += 1
                continue
            if char == Operators.CLOSING_PARENTHESIS:
                nesting_level -= 1
                continue
            if not is_inside_quote and not nesting_level and char == Operators.SPACE:
                operand_end = index + operand_start
                break
        return self.line[operand_start:operand_end], is_inside_quote, nesting_level

    def get_operand(self, *, continuing: bool = False, inside_quote: bool = False, previous_line_ending_with_l: bool = False,
                    nesting_level: int = 0) -> str:
        return self.get_operand_info(continuing, inside_quote, previous_line_ending_with_l, nesting_level)[0]

    def add_to_operand(self, string: str):
        self.operand_accumulator += string

    @property
    def operand(self) -> str:
        return self.operand_accumulator or self.get_operand()


class AssemblerLines:

    def __init__(self, strings: List[str]):
        self.lines: List[AssemblerLine] = [AssemblerLine(line) for line in strings]
        self.lines = self.remove_commented_out_lines()
        self.lines = self.combine_continuation_lines()

    def get_lines(self) -> List[AssemblerLine]:
        return self.lines

    def remove_commented_out_lines(self) -> List[AssemblerLine]:
        lines_without_comments: List[AssemblerLine] = list()
        continuing_comment: bool = bool()
        for line in self.lines:
            if not continuing_comment and not line.is_commented_out():
                lines_without_comments.append(line)
                continue
            if line.is_continuation_present() and line.is_commented_out():
                continuing_comment = True
                continue
            if continuing_comment and not line.is_continuation_present():
                continuing_comment = False
        return lines_without_comments

    def combine_continuation_lines(self) -> List[AssemblerLine]:
        combined_lines: List[AssemblerLine] = list()
        continuing: bool = False
        inside_quote: bool = False
        previous_line_ending_with_l: bool = False
        nesting_level: int = 0
        main_line: Optional[AssemblerLine] = None
        for line in self.lines:
            if not continuing and not line.is_continuation_present():
                combined_lines.append(line)
                continue
            operand, inside_quote, nesting_level = line.get_operand_info(continuing, inside_quote, previous_line_ending_with_l,
                                                                         nesting_level)
            if not continuing:
                main_line: AssemblerLine = line
                combined_lines.append(line)
            main_line.add_to_operand(operand)
            previous_line_ending_with_l = operand and operand[-1] in Operators.ATTRIBUTES
            if line.is_continuation_present():
                continuing = True
            elif continuing:
                continuing = False
                main_line = None
        return combined_lines
