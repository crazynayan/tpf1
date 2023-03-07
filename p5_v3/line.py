from typing import Tuple

from p5_v3.errors import ParserError


class AssemblerLine:
    SPACE = " "
    LABEL_START = 0
    CONTINUATION_START = 71
    QUOTE = "'"
    CONTINUING_START = 15

    def __init__(self, line):
        self.line: str = line

    def get_next_space(self, start_index: int) -> int:
        for index, char in enumerate(self.line[start_index:]):
            if char == self.SPACE:
                return index
        raise ParserError("AssemblerLine -> Next space not found.")

    def get_next_non_space(self, start_index: int) -> int:
        for index, char in enumerate(self.line[start_index:]):
            if char != self.SPACE:
                return index
        raise ParserError("AssemblerLine -> Next non space not found.")

    def is_label_present(self) -> bool:
        return self.line[self.LABEL_START] != self.SPACE

    @property
    def label_end(self) -> int:
        return self.get_next_space(self.LABEL_START)

    @property
    def label(self) -> str:
        return self.line[:self.label_end]

    @property
    def command_start(self) -> int:
        return self.get_next_non_space(self.label_end)

    @property
    def command_end(self) -> int:
        return self.get_next_space(self.command_start)

    @property
    def command(self) -> str:
        return self.line[self.command_start: self.command_end]

    @property
    def is_continuation_present(self) -> bool:
        return len(self.line) > self.CONTINUATION_START and self.line[self.CONTINUATION_START] != self.SPACE

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
            if not is_inside_quote and char == self.QUOTE and not possible_length_attribute:
                is_inside_quote = True
                continue
            if is_inside_quote and char == self.QUOTE:
                is_inside_quote = False
                continue
            if not is_inside_quote and char != self.SPACE:
                operand_end = index
                break
        return self.line[operand_start:operand_end], is_inside_quote

    @property
    def operand(self, *, continuing: bool = False, inside_quote: bool = False, previous_line_ending_with_l: bool = False) -> str:
        return self.get_operand_info(continuing, inside_quote, previous_line_ending_with_l)[0]

    def is_operand_inside_quote(self, *, continuing: bool = False, inside_quote: bool = False,
                                previous_line_ending_with_l: bool = False) -> bool:
        return self.get_operand_info(continuing, inside_quote, previous_line_ending_with_l)[1]
