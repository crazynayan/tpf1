import re
from typing import List

from firestore_ci import FirestoreDocument

from config import config
from p1_utils.file_line import Line
from p2_assembly.seg7_listing_line import ListingLine, create_listing_lines


class LstCmd(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.seg_name: str = str()  # 4 char name of the listing. Cannot be empty.
        self.stmt: str = str()
        self.source_stmt = str()
        self.label: str = str()
        self.command: str = str()
        self.operand: str = str()
        self.dsp: int = int()
        self.node_exception: bool = bool()

    @property
    def display_dsp(self) -> str:
        return " " * 5 if self.dsp == -1 else f"D{self.dsp:04X}"

    @property
    def display_node_ex(self) -> str:
        return "X" if self.node_exception else " "

    def __repr__(self):
        return f"{self.seg_name}:{self.stmt:7}:{self.source_stmt:7}: {self.display_dsp} :{self.display_node_ex}: " \
               f"{self.label:10}: {self.command:10}: {self.operand}"


LstCmd.init("listing_commands")


def create_listing_command(listing_line: ListingLine, seg_name) -> LstCmd:
    listing_command: LstCmd = LstCmd()
    listing_command.seg_name = seg_name
    listing_command.stmt = listing_line.stmt
    listing_command.source_stmt = listing_line.source_stmt
    listing_command.label = listing_line.label
    listing_command.dsp = listing_line.dsp
    listing_command.command = listing_line.command
    listing_command.operand = listing_line.operand
    return listing_command


def split_operand(operand: str) -> list:
    return re.split("[,'=()+-]", operand)


def create_listing_commands(seg_name: str, lines: List[str]) -> List[LstCmd]:
    listing_lines: List[ListingLine] = create_listing_lines(seg_name, lines)
    if not listing_lines:
        return list()
    equ_ds: set = {"EQU", "DS"}
    exec_macro_commands: set = {"GLOBZ"}  # Init with commands that require generated code
    ibm_cmds: set = {"DETAC", "FINIS", "FLIPC", "ATTAC"}
    exec_macro_ignored_commands: set = {"DS", "GFLDA", "ORG", "GL0AT", "GL0BP", "GL0BQ", "REGVAL", "SYSEQ", "REGEQ",
                                        "GL0BA", "GL0BB", "GL0BC", "GL0BD", "GL0BE", "GL0BF", "GL0BG", "GL0BY"}
    # Initialize the different type of source stmt
    ibm_source_stmt: set = {line.stmt for line in listing_lines if line.command in ibm_cmds and not line.source_stmt}
    exec_macro_source_stmt: set = {line.stmt for line in listing_lines if line.command in exec_macro_commands
                                   and not line.source_stmt}
    exec_ibm_source_stmt: set = exec_macro_source_stmt.union(ibm_source_stmt)
    data_macro_source_stmt: set = {line.source_stmt for line in listing_lines if line.source_stmt
                                   and line.command in {"DSECT", "USING"}
                                   and line.source_stmt not in exec_ibm_source_stmt}
    exec_ibm_data_macro_source_stmt: set = exec_ibm_source_stmt.union(data_macro_source_stmt)
    other_source_stm: set = {line.source_stmt for line in listing_lines if line.source_stmt
                             and line.source_stmt not in exec_ibm_data_macro_source_stmt}
    # Source commands = True Source - Data Macro declaration - Source commands that have been expanded
    source_commands: List[LstCmd] = [create_listing_command(line, seg_name) for line in listing_lines
                                     if not line.source_stmt
                                     and line.stmt not in exec_macro_source_stmt
                                     and not line.command.startswith("=")]
    source_labels: set = {label for cmd in source_commands for label in split_operand(cmd.operand) if label}
    # Exec cmds = Exec cmds that have been expanded - Ignored Exec cmds - EQU/DS cmds that are not used
    non_equ_ds_exec_commands: List[LstCmd] = [create_listing_command(line, seg_name) for line in listing_lines
                                              if line.source_stmt and line.source_stmt in exec_macro_source_stmt
                                              and line.command not in exec_macro_ignored_commands
                                              and line.command not in equ_ds]
    equ_ds_exec_commands: List[LstCmd] = [create_listing_command(line, seg_name) for line in listing_lines
                                          if line.source_stmt and line.source_stmt in exec_macro_source_stmt
                                          and line.command in equ_ds and line.label in source_labels]
    exec_commands: List[LstCmd] = non_equ_ds_exec_commands + equ_ds_exec_commands
    exec_labels: set = {label for cmd in exec_commands for label in split_operand(cmd.operand) if label}
    source_exec_labels: set = source_labels.union(exec_labels)
    # Data cmds = Generated USING,DSECT,CSECT + Generated EQU, DS that are used in source or exec cmds.
    using_ds_data_cmds: List[LstCmd] = [create_listing_command(line, seg_name) for line in listing_lines
                                        if line.source_stmt and line.source_stmt in data_macro_source_stmt
                                        and line.command in {"USING", "DSECT", "CSECT"}]
    push_pop_data_cmds: List[LstCmd] = [create_listing_command(line, seg_name) for line in listing_lines
                                        if line.source_stmt and line.source_stmt in data_macro_source_stmt
                                        and line.command in {"PUSH", "POP"} and line.operand.startswith("USING")]
    equ_ds_data_cmds: List[LstCmd] = [create_listing_command(line, seg_name) for line in listing_lines
                                      if line.source_stmt and line.source_stmt in data_macro_source_stmt
                                      and line.command in equ_ds and line.label in source_exec_labels]
    data_commands: List[LstCmd] = using_ds_data_cmds + equ_ds_data_cmds + push_pop_data_cmds
    # Other cmds = EQU generated from Exec commands that have not been expanded and that are being used - EQU from IBM
    other_commands: List[LstCmd] = [create_listing_command(line, seg_name) for line in listing_lines
                                    if line.source_stmt and line.source_stmt in other_source_stm
                                    and line.command == "EQU" and line.label in source_labels]
    listing_commands: List[LstCmd] = source_commands + exec_commands + data_commands + other_commands
    listing_commands.sort(key=lambda item: item.stmt)
    # Setup node exception
    node_exception_cmds: set = {"BEGIN", "PGMID", "WA0AA"}
    node_exception_stmt: set = {line.stmt for line in listing_lines if line.command in node_exception_cmds
                                and not line.source_stmt}
    for cmd in listing_commands:
        if cmd.source_stmt and cmd.source_stmt in node_exception_stmt:
            cmd.node_exception = True
        if cmd.command in node_exception_cmds:
            cmd.node_exception = True
    directive_plus_ignored_cmds: set = config.DIRECTIVE.union({"DSHDR", "REGVAL", "REGEQ", "#UEXIT", "#LEVL",
                                                               "#URTRN", "IFL0DF", "DFGDS", "DFTDC"})
    for source_stmt in data_macro_source_stmt:
        exec_lines: List[str] = list()
        ignore_inside_dsect: bool = False
        generated_lines: List[ListingLine] = [line for line in listing_lines if line.source_stmt == source_stmt]
        for line in generated_lines:
            if line.command == "DSECT":
                ignore_inside_dsect = True
            elif line.command == "CSECT":
                ignore_inside_dsect = False
            if not ignore_inside_dsect and line.command not in directive_plus_ignored_cmds:
                exec_lines.append(line.command)
        if not exec_lines:
            cmd = next(cmd for cmd in listing_commands if cmd.stmt == source_stmt)
            cmd.node_exception = True
    #     elif source_stmt == " 15669":
    #         print(exec_lines)
    # with open(f"tmp/{seg_name}-extract.txt", "w") as fh:
    #     fh.writelines(f"{str(line)}\n" for line in listing_commands)
    return listing_commands


def create_line(listing_command: LstCmd) -> Line:
    line = Line()
    line.label = listing_command.label
    line.command = listing_command.command
    line.operand = listing_command.operand
    line.dsp = listing_command.dsp
    line.node_exception = listing_command.node_exception
    line.index = int(listing_command.stmt.strip())
    return line


def get_lines_from_listing_commands(listing_commands: List[LstCmd]) -> List[Line]:
    return [create_line(command) for command in listing_commands]
