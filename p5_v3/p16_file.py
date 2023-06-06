import os.path
from os.path import exists
from typing import List

from p5_v3.p01_errors import SourceFileNotFound


class File:
    ASSEMBLER = "asm"
    LISTING = "lst"
    MACRO = "mac"

    def __init__(self, filename: str):
        self.filename = filename

    @property
    def file_type(self) -> str:
        return self.filename[-3:]

    @property
    def name_four_char(self) -> str:
        return os.path.basename(self.filename)[:4].upper()

    def is_valid(self) -> bool:
        return self.file_type in (self.ASSEMBLER, self.LISTING, self.MACRO)

    def open(self) -> List[str]:
        try:
            with open(self.filename, "r", errors="replace") as file:
                return file.readlines()
        except FileNotFoundError:
            raise SourceFileNotFound

    def exists(self) -> bool:
        return exists(self.filename)

    def get_name(self) -> str:
        return self.name_four_char if self.file_type in (self.ASSEMBLER or self.LISTING) else self.filename[:-4].upper()


class Preprocessor:
    PREFIX_CHAR = "0"
    FIRST_TWO_CHAR_IN_CVS_HEADER = ["==", "Ch", "RC", "VE", "**"]
    LEN_OF_HEADER = len(FIRST_TWO_CHAR_IN_CVS_HEADER)
    LEN_OF_PREFIX_TO_REMOVE = 7

    def __init__(self):
        self.lines: List[str] = list()

    def process(self):
        self.remove_empty_lines()
        self.make_it_upper_case()
        self.remove_trailing_newline_char()

    def get_lines(self) -> List[str]:
        return self.lines

    def remove_empty_lines(self) -> None:
        self.lines = [line for line in self.lines if line.strip()]

    def make_it_upper_case(self) -> None:
        self.lines = [line.upper() for line in self.lines]

    def remove_trailing_newline_char(self):
        self.lines = [line.strip("\n") for line in self.lines]


class FilePreprocessor(Preprocessor):

    def __init__(self, filename):
        super().__init__()
        file = File(filename)
        self.lines = file.open()
        if file.file_type in (file.ASSEMBLER, file.MACRO) and self.is_cvs_file():
            self.remove_cvs_tags()
        self.process()

    def is_cvs_file(self) -> bool:
        if self.FIRST_TWO_CHAR_IN_CVS_HEADER != [line[:2] for line in self.lines[:self.LEN_OF_HEADER]]:
            return False
        return all(line[0] == self.PREFIX_CHAR for line in self.lines[self.LEN_OF_HEADER:] if line.strip())

    def remove_cvs_tags(self) -> None:
        self.lines = [line[self.LEN_OF_PREFIX_TO_REMOVE:] for line in self.lines[self.LEN_OF_HEADER:] if line.strip()]


class StreamPreprocessor(Preprocessor):

    def __init__(self, buffer: str):
        super().__init__()
        self.lines = buffer.split("\n")
        self.process()
