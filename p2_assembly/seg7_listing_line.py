from enum import Enum, auto
from typing import List, Optional


class Continuation(Enum):
    NO_CONTINUATION = auto()
    IN_QUOTES = auto()
    COMMA_ENDING = auto()
    DIRECT = auto()
    COMMENT = auto()


class ListingLine:

    def __init__(self):
        self.stmt: str = str()  # stmt: 6 digit id from listing with leading spaces. Continuing lines will be blank.
        self.line: str = str()  # The complete line from the listing. Cannot be empty.
        self.source_stmt: str = str()  # Only for generated line. Empty for normal line.
        self.label: str = str()
        self.dsp: int = -1
        self.command: str = str()
        self.operand: str = str()
        self.continuation_type: Continuation = Continuation.NO_CONTINUATION

    def __repr__(self):
        return f"{self.stmt:7}:{self.source_stmt:7}:{self.label:10}({self.dsp:3}):{self.command:10}:" \
               f"{self.operand:30}:{self.line}"

    @property
    def is_continuation(self) -> bool:
        return len(self.line) > 121 and self.line[121] != " "

    @property
    def is_comment(self) -> bool:
        return len(self.line) > 50 and self.line[50] in {".", "*"}

    @property
    def is_generated(self) -> bool:
        return len(self.line) > 49 and self.line[49] == "+"

    @property
    def is_loc_present(self) -> bool:
        return self.line[1:9] != 8 * " "

    @property
    def is_machine_code(self) -> bool:
        return self.is_loc_present and self.line[10:12] != 2 * " "

    @property
    def loc(self) -> int:
        try:
            return int(self.line[1:9], 16) if self.is_loc_present else -1
        except ValueError:
            return -1

    @property
    def is_addr1_present(self) -> bool:
        return self.line[25:33] != 8 * " "

    @property
    def addr1(self) -> int:
        try:
            return int(self.line[25:33], 16) if self.is_addr1_present else -1
        except ValueError:
            return -1

    def is_valid_assembler(self, seg_name) -> bool:
        if not self.line.strip():
            return False
        if len(self.line) > 9 and self.line[3:6] in {"Act", "Loc"}:
            return False
        if len(self.line) > 15 and self.line[11:15] == seg_name:
            return False
        return True

    def set_line_stmt(self, line) -> None:
        self.line = line.rstrip()
        stmt: str = line[43:49] if len(line) > 49 else str()
        stripped_stmt: str = stmt.strip()
        if stmt and stmt[-1].isdigit() and stripped_stmt.isdigit() and int(stripped_stmt) != 0:
            self.stmt = stmt

    def get_index_to_char_start(self, start_index):
        return next((index + start_index for index, char in enumerate(self.line[start_index:121]) if char != " "), None)

    def get_index_to_char_end(self, start_index):
        return next((index + start_index for index, char in enumerate(self.line[start_index:121]) if char == " "), None)

    def set_label_command_operand(self, prev_line_typ: Continuation):
        if len(self.line) < 52:
            return str()
        if prev_line_typ == Continuation.COMMENT:
            if self.is_continuation:
                self.continuation_type = Continuation.COMMENT
            return
        if prev_line_typ == Continuation.NO_CONTINUATION:
            if self.line[50] != " ":
                label_end_index = self.get_index_to_char_end(50)
                if label_end_index is None:
                    return
                self.label = self.line[50:label_end_index].upper()
            else:
                label_end_index = 51
            command_start_index = self.get_index_to_char_start(label_end_index)
            if command_start_index is None:
                return
            command_end_index = self.get_index_to_char_end(command_start_index)
            if command_end_index is None:
                command_end_index = 121
            self.command = self.line[command_start_index:command_end_index].upper()
            self.dsp = self.loc
            if self.dsp == -1:
                self.dsp = self.addr1
        else:
            command_end_index = 51
        if prev_line_typ in (Continuation.DIRECT, Continuation.IN_QUOTES):
            operand_start_index = 65
        else:
            operand_start_index = self.get_index_to_char_start(command_end_index)
            if operand_start_index is None:
                return str()
        prev_char = self.line[operand_start_index - 1]
        in_quotes = True if prev_line_typ == Continuation.IN_QUOTES else False
        chars = list()
        for char in self.line[operand_start_index:121]:
            if not in_quotes and char == " ":
                break
            chars.append(char)
            if char == "'":
                if not in_quotes and prev_char != "L":
                    in_quotes = True
                elif in_quotes:
                    in_quotes = False
            prev_char = char
        if self.is_continuation:
            if in_quotes:
                self.continuation_type = Continuation.IN_QUOTES
            elif chars[-1] == ",":
                self.continuation_type = Continuation.COMMA_ENDING
            elif len(chars) == 121 - operand_start_index:
                self.continuation_type = Continuation.DIRECT
            else:
                self.continuation_type = Continuation.COMMENT
        self.operand = "".join(chars).upper()


def create_listing_lines(seg_name: str, lines: List[str]) -> List[ListingLine]:
    listing_lines: List[ListingLine] = list()
    source_stmt: str = str()
    continuing_comment: bool = False
    macro_mend_skip: bool = False
    main_line: Optional[ListingLine] = None
    prev_continuation_type: Continuation = Continuation.NO_CONTINUATION
    for line in lines:
        listing_line = ListingLine()
        listing_line.set_line_stmt(line)
        # Reject invalid lines and comments
        if not listing_line.is_valid_assembler(seg_name):
            continue
        if not listing_line.stmt and not main_line:
            continue
        if listing_line.is_comment or continuing_comment:
            continuing_comment = True if listing_line.is_continuation else False
        if listing_line.is_comment or continuing_comment:
            continue
        # Setup label, command and operands
        listing_line.set_label_command_operand(prev_continuation_type)
        # Skip code between MACRO and MEND
        if listing_line.command == "MACRO":
            macro_mend_skip = True
        if macro_mend_skip:
            if listing_line.command == "MEND":
                macro_mend_skip = False
            continue
        # Merge operands of continuing list
        if main_line:
            main_line.operand += listing_line.operand
        if listing_line.is_continuation:
            if not main_line:
                main_line = listing_line
            prev_continuation_type = listing_line.continuation_type
        elif main_line:
            main_line = None
            prev_continuation_type = Continuation.NO_CONTINUATION
        # Setup source_stmt for generated lines
        if listing_line.is_generated:
            listing_line.source_stmt = source_stmt
        elif listing_line.stmt:
            source_stmt = listing_line.stmt
        if listing_line.stmt and listing_line.command:
            listing_lines.append(listing_line)
    # Second pass to remove lines that do NOT have dsp.
    listing_lines = [line for line in listing_lines if not line.is_generated
                     or (line.dsp != -1 and line.command not in {"ORG"})
                     or (line.command in {"PUSH", "POP"} and line.operand == "USING")]
    return listing_lines
