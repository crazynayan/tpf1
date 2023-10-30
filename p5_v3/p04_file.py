import os.path
from os.path import exists
from typing import List

from p5_v3.p00_config import FileTag
from p5_v3.p01_errors import SourceFileNotFound


class File:

    def __init__(self, filename: str):
        self.filename = filename

    @property
    def file_type(self) -> str:
        return self.filename[-3:]

    @property
    def name_four_char(self) -> str:
        return os.path.basename(self.filename)[:4].upper()

    def is_valid(self) -> bool:
        return self.file_type in (FileTag.ASSEMBLER, FileTag.LISTING, FileTag.MACRO)

    def open(self) -> List[str]:
        try:
            with open(self.filename, "r", errors="replace") as file:
                return file.readlines()
        except FileNotFoundError:
            raise SourceFileNotFound

    def exists(self) -> bool:
        return exists(self.filename)

    def is_segment(self) -> bool:
        return self.file_type in (FileTag.ASSEMBLER or FileTag.LISTING)

    def is_macro(self) -> bool:
        return self.file_type == FileTag.MACRO

    def get_name(self) -> str:
        return self.name_four_char if self.is_segment() else os.path.basename(self.filename)[:-4].upper()


class FilePath:

    def __init__(self, file_path: str):
        self.file_path: str = file_path

    def is_directory(self):
        return os.path.isdir(self.file_path)

    def get_file_list(self):
        if not self.is_directory():
            raise SourceFileNotFound
        return os.listdir(self.file_path)

    def get_segment_list(self) -> List[str]:
        filenames: List[str] = self.get_file_list()
        segment_filenames: List[str] = [filename for filename in filenames if File(filename).is_segment()]
        return [File(filename).get_name() for filename in segment_filenames]

    def get_macro_list(self) -> List[str]:
        filenames: List[str] = self.get_file_list()
        segment_filenames: List[str] = [filename for filename in filenames if File(filename).is_macro()]
        return [File(filename).get_name() for filename in segment_filenames]


class Preprocessor:
    PREFIX_CHAR = "0"
    FIRST_TWO_CHAR_IN_CVS_HEADER = ["==", "Ch", "RC", "VE", "**"]
    LEN_OF_HEADER = len(FIRST_TWO_CHAR_IN_CVS_HEADER)
    LEN_OF_PREFIX_TO_REMOVE = 7

    def __init__(self):
        self.lines: List[str] = list()

    def process(self):
        self.make_it_upper_case()
        self.remove_trailing_newline_char()

    def get_lines(self) -> List[str]:
        return self.lines

    def make_it_upper_case(self) -> None:
        self.lines = [line.upper() for line in self.lines]

    def remove_trailing_newline_char(self):
        self.lines = [line.strip("\n") for line in self.lines]


class FilePreprocessor(Preprocessor):

    def __init__(self, filename):
        super().__init__()
        file = File(filename)
        self.lines = file.open()
        if file.file_type in (FileTag.ASSEMBLER, FileTag.MACRO) and self.is_cvs_file():
            self.remove_cvs_tags()
        self.process()

    def is_cvs_file(self) -> bool:
        if self.FIRST_TWO_CHAR_IN_CVS_HEADER != [line[:2] for line in self.lines[:self.LEN_OF_HEADER]]:
            return False
        return all(line[0] == self.PREFIX_CHAR for line in self.lines[self.LEN_OF_HEADER:] if line.strip())

    def remove_cvs_tags(self) -> None:
        self.lines = [line[self.LEN_OF_PREFIX_TO_REMOVE:] for line in self.lines[self.LEN_OF_HEADER:]]


class StreamPreprocessor(Preprocessor):

    def __init__(self, buffer: str):
        super().__init__()
        self.lines = buffer.split("\n")
        self.process()
