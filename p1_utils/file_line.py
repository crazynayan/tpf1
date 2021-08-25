import re
from typing import List, Optional, Dict

from config import config


class File:

    @staticmethod
    def _get_line(word: str, lines: List[str]) -> Optional[str]:
        line: Optional[str] = next((line for line in lines if line[50:].strip().split()[0] == word), None)
        return line

    def __init__(self, filename: str):
        self.lines: List[str] = list()
        self.macros: Dict[str, list] = dict()  # Macro names -> Listing generated macros
        # Open the file
        try:
            with open(filename, "r", errors="replace") as file:
                lines = file.readlines()
        except FileNotFoundError:
            return
        # Check for listing
        if filename[-4:] == ".lst":
            lines = [line[:-1].upper() for line in lines if len(line) >= 50 and line[48].isdigit()
                     and line[49] in {" ", "+"} and not line.startswith("   Active Usings")]
            # Remove everything after FINIS/ORG
            finis = self._get_line("FINIS", lines)
            ltorg = self._get_line("LTORG", lines)
            end_line = ltorg if ltorg else finis
            lines = lines[:lines.index(end_line)]
            # Remove all code between MACRO and MEND
            macro = self._get_line("MACRO", lines)
            while macro:
                mend = self._get_line("MEND", lines)
                lines = lines[:lines.index(macro)] + lines[lines.index(mend) + 1:]
                macro = self._get_line("MACRO", lines)
            # Extract data macros (Only REG=) TODO: DATAS
            macros = [line for line in lines if len(line[50:].strip().split()) > 1
                      and line[50:].strip().split()[1].startswith("REG=")]
            macro_dict = dict()
            for line in macros:
                macro_name = line[50:].strip().split()[0]
                if macro_name in macro_dict:
                    continue
                macro_dict[macro_name] = line
            for macro_name, macro_line in macro_dict.items():
                self.macros[macro_name] = list()
                for line in lines[lines.index(macro_line) + 1:]:
                    if line[49] != "+":
                        break
                    if line[50] in config.COMMENT_C1:
                        continue
                    self.macros[macro_name].append(line[50:])
            # Truncate all starting characters to match CC=1 for assembly
            lines = [line[50:] for line in lines if line[49] == " "]
        # Remove the CVS header if present
        index = 0
        for line in lines:
            if line[:2] not in config.CVS_C2:
                break
            index += 1
        lines = lines[index:] if index < len(lines) else list()
        # Remove empty lines and trailing new line character & make everything upper case
        lines = [line.strip("\n").upper() for line in lines if line.strip()]
        if not lines:
            return
        # Find the character that is added by CVS on each line
        char = str()
        if all(line[0] == lines[0][0] for line in lines):
            char = lines[0][0]
        # Remove (TRIM) the character from each line
        if char in config.TRIM:
            lines = [line[config.TRIM[char]:] for line in lines]
        # Remove comments
        lines = [line for line in lines if line.strip() and line[0] not in config.COMMENT_C1]
        self.lines = lines
        return


class Line:
    def __init__(self):
        self.label: Optional[str] = None
        self.command: Optional[str] = None
        self.operand: Optional[str] = None
        self.continuation: bool = False
        self.quote_continuation: bool = False
        self.index: Optional[int] = None

    @classmethod
    def from_line(cls, file_line: str, continuing: bool = False, quote_continuing: bool = False) -> "Line":
        # Create a line object from a single file line.
        line = cls()
        if len(file_line) > 71 and file_line[71] != " ":
            line.continuation = True
            file_line = file_line[:71]
        if quote_continuing:
            all_words = file_line.split()
            words = list()
            for word in all_words:
                words.append(word)
                if word[-1] == "'":
                    break
            words = [" ".join(words)]
        elif line.continuation and "'" in file_line and file_line.count("'") % 2 != 0:
            # This is the case where 2 quotes are in separate lines for e.g. MSG='.... X and in next line ...'
            line.quote_continuation = True
            file_line = file_line + "'"
            words = re.findall(r"(?:'.*?'|\S)+", file_line)
            words[-1] = words[-1][:-1]
        else:
            # Split the line in words. Keep words within single quotes together.
            words = re.findall(r"(?:[^L\s]'[^']*'|\S)+", file_line)
        if file_line[0] == " ":
            # The label is None for lines with first character space (No label)
            words.insert(0, None)
        if continuing:
            # The command is None for continued lines
            words.insert(0, None)
        line.label = words[0]
        line.command = words[1] if len(words) > 1 else None
        line.operand = words[2] if len(words) > 2 else None
        return line

    @classmethod
    def from_file(cls, file_lines: List[str]) -> List["Line"]:
        # Create a list of Line objects. Also combines multiple continuing lines in a single line object.
        lines = list()
        prior_line = Line()
        main_line = None
        for file_line in file_lines:
            line = cls.from_line(file_line, prior_line.continuation, prior_line.quote_continuation)
            if not prior_line.continuation:
                lines.append(line)
                main_line = line
            else:
                main_line.operand = main_line.operand + line.operand if main_line.operand is not None else line.operand
            prior_line = line
        return lines

    def remove_suffix(self) -> "Line":
        self.label = next(iter(self.label.split("&"))) if self.label is not None else None
        return self

    @property
    def is_first_pass(self) -> bool:
        return True if self.is_assembler_directive and self.command not in config.DIRECTIVE_SECOND_PASS else False

    @property
    def is_assembler_directive(self) -> bool:
        return True if self.command in config.DIRECTIVE else False

    @property
    def create_node_for_directive(self) -> bool:
        return True if self.command in config.DIRECTIVE_NODE else False

    @property
    def is_sw00sr(self) -> bool:
        return True if self.command in config.SW00SR else False

    @property
    def instruction_length(self) -> int:
        if self.is_assembler_directive:
            return 0
        if self.command in config.INSTRUCTION_LEN_2:
            return 2
        if self.command in config.INSTRUCTION_LEN_6:
            return 6
        return config.INSTRUCTION_LEN_DEFAULT

    @property
    def is_fall_down(self) -> bool:
        return True if self.command not in config.NO_FALL_DOWN else False

    def split_operands(self) -> List[str]:
        # Split operands separated by commas. Ignore commas enclosed in parenthesis or quotes.
        # Take care L' does NOT start a quote
        if not self.operand:
            return list()
        ignore_commas, in_parenthesis, in_quotes = False, False, False
        new_operand: List = list()
        prev_char: str = str()
        for char in self.operand:
            if ignore_commas is False:
                if char == "(":
                    ignore_commas = True
                    in_parenthesis = True
                elif char == "'" and prev_char != "L":
                    ignore_commas = True
                    in_quotes = True
            elif char == ")" and in_parenthesis:
                ignore_commas = False
                in_parenthesis = False
            elif char == "'" and in_quotes:
                ignore_commas = False
                in_quotes = False
            updated_char = "|" if char == "," and ignore_commas is False else char
            prev_char = char
            new_operand.append(updated_char)
        return "".join(new_operand).split("|")

    def __repr__(self) -> str:
        return f"{self.label}:{self.command}:{self.operand}"
