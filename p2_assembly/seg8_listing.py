import re
from typing import List

from firestore_ci import FirestoreDocument

from p2_assembly.seg7_listing_line import ListingLine, create_listing_lines


class ListingCommand(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.seg_name: str = str()  # 4 char name of the listing. Cannot be empty.
        self.stmt: str = str()
        self.source_stmt = str()
        self.label: str = str()
        self.command: str = str()
        self.operand: str = str()
        self.dsp: int = int()

    @property
    def display_dsp(self) -> str:
        return " " * 5 if self.dsp == -1 else f"D{self.dsp:04}"

    def __repr__(self):
        return f"{self.seg_name}:{self.stmt:7}:{self.source_stmt:7}:{self.display_dsp}:" \
               f"{self.label:10}:{self.command:10}:{self.operand}"


ListingCommand.init("listing_commands")


def create_listing_command(listing_line: ListingLine, seg_name) -> ListingCommand:
    listing_command: ListingCommand = ListingCommand()
    listing_command.seg_name = seg_name
    listing_command.stmt = listing_line.stmt
    listing_command.source_stmt = listing_line.source_stmt
    listing_command.label = listing_line.label
    listing_command.dsp = listing_line.dsp
    listing_command.command = listing_line.command
    listing_command.operand = listing_line.operand
    return listing_command


def create_listing_commands(seg_name: str) -> List[ListingCommand]:
    listing_lines: List[ListingLine] = create_listing_lines(seg_name)
    if not listing_lines:
        return list()
    generated_commands: set = {"GLOBZ"}  # Init with commands that require generated code
    needed_generated_stmts: set = {line.stmt for line in listing_lines if line.command in generated_commands
                                   and not line.source_stmt}
    listing_commands: List[ListingCommand] = [create_listing_command(line, seg_name) for line in listing_lines
                                              if (line.source_stmt and line.source_stmt in needed_generated_stmts)
                                              or (not line.source_stmt and line.command not in generated_commands)]
    ignored_commands: set = {"DS", "GFLDA", "ORG", "GL0AT", "GL0BP", "GL0BQ", "REGVAL", "SYSEQ", "REGEQ", "GL0BA",
                             "GL0BB", "GL0BC", "GL0BD", "GL0BE", "GL0BF", "GL0BG"}
    listing_commands: List[ListingCommand] = [command for command in listing_commands
                                              if not command.source_stmt or command.label
                                              or command.command not in ignored_commands]
    listing_commands: List[ListingCommand] = [command for command in listing_commands
                                              if not command.command.startswith("=")]
    operand_labels: set = {label for listing_command in listing_commands
                           for label in re.split("[,=()+-]", listing_command.operand)}
    label_commands: List[ListingCommand] = [create_listing_command(line, seg_name) for line in listing_lines
                                            if line.source_stmt and line.source_stmt not in needed_generated_stmts
                                            and line.label and line.label in operand_labels]
    listing_commands += label_commands
    listing_commands: List[ListingCommand] = [command for command in listing_commands if not command.source_stmt
                                              or not command.label or command.label in operand_labels
                                              or command.command not in {"DS", "EQU"}]
    listing_commands.sort(key=lambda item: item.stmt)
    with open(f"{seg_name}.txt", "w") as fh:
        fh.writelines(f"{str(line)}\n" for line in listing_commands)
    return listing_commands
