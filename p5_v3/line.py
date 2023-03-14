from typing import Tuple, List, Optional

from p5_v3.base_parser import Operators
from p5_v3.errors import ParserError


class AssemblerLine:
    LABEL_START = 0
    CONTINUATION_START = 71
    CONTINUING_START = 15
    COMMENTED_OUT_CHARS = {"*", "."}

    def __init__(self, line):
        self.line: str = line
        self.operand_accumulator: str = str()

    def __repr__(self):
        return f"{self.label}:{self.command}:{self.operand}"

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
    def command_start(self) -> int:
        try:
            return self.get_next_non_space(self.label_end)
        except ParserError:
            return len(self.line)

    @property
    def command_end(self) -> int:
        try:
            return self.get_next_space(self.command_start)
        except ParserError:
            return len(self.line)

    @property
    def command(self) -> str:
        return self.line[self.command_start: self.command_end]

    def is_commented_out(self) -> bool:
        return self.line[self.LABEL_START] in self.COMMENTED_OUT_CHARS

    def is_continuation_present(self) -> bool:
        return len(self.line) > self.CONTINUATION_START and self.line[self.CONTINUATION_START] != Operators.SPACE

    def get_operand_info(self, continuing: bool, inside_quote: bool, previous_line_ending_with_l: bool) -> Tuple[str, bool]:
        try:
            operand_start = self.CONTINUING_START if continuing else self.get_next_non_space(self.command_end)
        except ParserError:
            return str(), False
        if operand_start >= self.CONTINUATION_START:
            return str(), False
        is_inside_quote = inside_quote
        operand_end = self.CONTINUATION_START
        for index, char in enumerate(self.line[operand_start:self.CONTINUATION_START]):
            possible_length_attribute = self.line[operand_start + index - 1] == "L" if index > 0 else previous_line_ending_with_l
            if not is_inside_quote and char == Operators.QUOTE and not possible_length_attribute:
                is_inside_quote = True
                continue
            if is_inside_quote and char == Operators.QUOTE:
                is_inside_quote = False
                continue
            if not is_inside_quote and char == Operators.SPACE:
                operand_end = index + operand_start
                break
        return self.line[operand_start:operand_end], is_inside_quote

    def get_operand(self, *, continuing: bool = False, inside_quote: bool = False, previous_line_ending_with_l: bool = False) -> str:
        return self.get_operand_info(continuing, inside_quote, previous_line_ending_with_l)[0]

    def add_to_operand(self, string: str):
        self.operand_accumulator += string

    @property
    def operand(self) -> str:
        return self.operand_accumulator or self.get_operand()


class AssemblerLines:

    def __init__(self, strings: List[str]):
        self.lines: List[AssemblerLine] = [AssemblerLine(line) for line in strings]

    def process(self) -> List[AssemblerLine]:
        self.lines = self.remove_commented_out_lines()
        self.lines = self.combine_continuation_lines()
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
        main_line: Optional[AssemblerLine] = None
        for line in self.lines:
            if not continuing and not line.is_continuation_present():
                combined_lines.append(line)
                continue
            operand, inside_quote = line.get_operand_info(continuing=continuing, inside_quote=inside_quote,
                                                          previous_line_ending_with_l=previous_line_ending_with_l)
            if not continuing:
                main_line: AssemblerLine = line
                combined_lines.append(line)
            main_line.add_to_operand(operand)
            previous_line_ending_with_l = operand and operand[-1] == Operators.LENGTH_SYMBOL
            if line.is_continuation_present():
                continuing = True
            elif continuing:
                continuing = False
                main_line = None
        return combined_lines
